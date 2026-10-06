"""FDAAA 801 Final Rule results-reporting clock.

The statute (42 U.S.C. 282(j)) and the 2016 Final Rule (42 CFR Part 11) require
results information for an applicable clinical trial within 12 months of the
primary completion date, unless a certified delay applies. Phase 0 implements
the clock only: completion-date type, the applicable-trial flag, and a
time-aware due date. Certified delays, good-cause extensions, and live
ClinicalTrials.gov legal-status fields are unmeasured.

The reference date is committed as 2026-10-06 so harnesses are deterministic.
A trial that completed three months before that date is not late.
"""

from __future__ import annotations

import calendar
from datetime import date

from silent_trials import REFERENCE_DATE_ISO
from silent_trials.schemas import FdaaaClock, FdaaaStatus, TrialRecord

RESULTS_DUE_MONTHS = 12
REFERENCE_DATE = date.fromisoformat(REFERENCE_DATE_ISO)


def add_months(day: date, months: int) -> date:
    year = day.year + (day.month - 1 + months) // 12
    month = (day.month - 1 + months) % 12 + 1
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(day.day, last))


def derive_applicable(trial: TrialRecord) -> bool:
    """Recompute the ACT flag from structured fields.

    The committed ``applicable_clinical_trial`` field is authoritative for
    scoring. This helper exists so a later ingest can explain the flag. It
    is a simplified stand-in, not the full 42 CFR 11.22 checklist.
    """

    if trial.study_type != "interventional":
        return False
    if trial.device_feasibility:
        return False
    if trial.phase in {"Phase 1", "Early Phase 1"} and trial.product_type in {
        "drug",
        "biologic",
    }:
        return False
    if trial.phase == "Not Applicable" and trial.product_type == "behavioral":
        return False
    return trial.us_site or trial.fda_regulated


def completion_for_clock(trial: TrialRecord) -> date:
    """FDAAA uses the primary completion date, not the study completion date."""

    if trial.completion_date_type == "study":
        if trial.study_completion_date is not None:
            return trial.study_completion_date
        return trial.primary_completion_date
    return trial.primary_completion_date


def evaluate_clock(
    trial: TrialRecord,
    *,
    reference: date = REFERENCE_DATE,
    matched_publication: bool = False,
) -> FdaaaClock:
    """Return the time-aware reporting status for one trial."""

    applicable = trial.applicable_clinical_trial
    completion = completion_for_clock(trial)
    days_elapsed = (reference - completion).days
    due_date: date | None = None
    days_remaining: int | None = None
    status: FdaaaStatus
    rationale: str

    if not applicable:
        status = "NOT_APPLICABLE"
        rationale = (
            "Not an applicable clinical trial under the committed ACT flag. "
            "FDAAA results deadline does not attach."
        )
    else:
        due_date = add_months(completion, RESULTS_DUE_MONTHS)
        days_remaining = (due_date - reference).days
        if trial.has_registry_results and matched_publication:
            status = "REPORTED_BOTH"
            rationale = (
                f"Registry results posted ({trial.registry_results_first_posted}) "
                "and a matched publication exists."
            )
        elif trial.has_registry_results:
            status = "REPORTED_REGISTRY"
            rationale = (
                "Results information is posted to the registry. Absence of a "
                "journal article does not make this trial silent."
            )
        elif days_remaining > 0:
            status = "NOT_YET_DUE"
            rationale = (
                f"Primary completion {completion.isoformat()} plus "
                f"{RESULTS_DUE_MONTHS} months is {due_date.isoformat()}. "
                f"{days_remaining} days remain as of {reference.isoformat()}."
            )
        elif matched_publication:
            status = "REPORTED_PUBLICATION"
            rationale = (
                "Past the 12-month deadline with no registry results, but a "
                "matched journal publication exists."
            )
        else:
            status = "SILENT"
            rationale = (
                f"Applicable trial, primary completion {completion.isoformat()}, "
                f"due {due_date.isoformat()}, no registry results and no "
                "matched publication as of the reference date."
            )

    return FdaaaClock(
        nct_id=trial.nct_id,
        reference_date=reference,
        completion_date=completion,
        completion_date_type=trial.completion_date_type,
        applicable=applicable,
        due_date=due_date,
        days_elapsed=days_elapsed,
        days_remaining=days_remaining,
        has_registry_results=trial.has_registry_results,
        status=status,
        rationale=rationale,
    )
