"""Combine the FDAAA clock with the matcher to label one trial."""

from __future__ import annotations

from datetime import date

from silent_trials.fdaaa import REFERENCE_DATE, evaluate_clock
from silent_trials.matcher import match_trial
from silent_trials.schemas import (
    FdaaaStatus,
    MatchResult,
    PublicationRecord,
    ReportingOutcome,
    TrialRecord,
)


def combine_outcome(
    trial: TrialRecord,
    match: MatchResult,
    *,
    reference: date = REFERENCE_DATE,
) -> ReportingOutcome:
    matched = match.decision == "MATCH"
    clock = evaluate_clock(trial, reference=reference, matched_publication=matched)
    outcome: FdaaaStatus = clock.status
    if clock.status == "NOT_YET_DUE" and match.decision == "AMBIGUOUS":
        outcome = "NOT_YET_DUE"
    return ReportingOutcome(
        nct_id=trial.nct_id,
        sponsor=trial.sponsor,
        clock=clock,
        match=match,
        outcome=outcome,
    )


def report_trial(
    trial: TrialRecord,
    publications: list[PublicationRecord],
    *,
    reference: date = REFERENCE_DATE,
) -> ReportingOutcome:
    match = match_trial(trial, publications)
    return combine_outcome(trial, match, reference=reference)


def sponsor_counts(rows: list[ReportingOutcome]) -> dict[str, dict[str, int]]:
    """Count outcomes by sponsor. Designed-probe tallies, not a live ranking."""

    out: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = out.setdefault(
            row.sponsor,
            {"n": 0, "silent": 0, "reported": 0, "not_yet_due": 0, "not_applicable": 0},
        )
        bucket["n"] += 1
        if row.outcome == "SILENT":
            bucket["silent"] += 1
        elif row.outcome in {"REPORTED_REGISTRY", "REPORTED_PUBLICATION", "REPORTED_BOTH"}:
            bucket["reported"] += 1
        elif row.outcome == "NOT_YET_DUE":
            bucket["not_yet_due"] += 1
        else:
            bucket["not_applicable"] += 1
    return out
