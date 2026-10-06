from __future__ import annotations

from datetime import date

from silent_trials.cli import load_samples
from silent_trials.fdaaa import (
    REFERENCE_DATE,
    add_months,
    completion_for_clock,
    derive_applicable,
    evaluate_clock,
)
from silent_trials.matcher import match_trial
from silent_trials.reporting import combine_outcome, report_trial, sponsor_counts


def _sample(sample_id: str):
    return next(s for s in load_samples() if s.sample_id == sample_id)


def test_reference_date_is_committed() -> None:
    assert date(2026, 10, 6) == REFERENCE_DATE


def test_four_months_ago_is_not_due() -> None:
    sample = _sample("S3-not-yet-due")
    clock = evaluate_clock(sample.trial)
    assert clock.status == "NOT_YET_DUE"
    assert clock.days_remaining is not None
    assert clock.days_remaining > 0
    assert clock.due_date == date(2027, 6, 6)


def test_three_months_ago_is_not_late() -> None:
    sample = _sample("S10-three-months-not-late")
    clock = evaluate_clock(sample.trial)
    assert clock.status == "NOT_YET_DUE"
    assert clock.due_date == date(2027, 7, 6)


def test_registry_results_are_not_silent() -> None:
    sample = _sample("S4-registry-only")
    clock = evaluate_clock(sample.trial)
    assert clock.status == "REPORTED_REGISTRY"


def test_phase1_not_applicable() -> None:
    sample = _sample("S7-phase1-not-applicable")
    clock = evaluate_clock(sample.trial)
    assert clock.status == "NOT_APPLICABLE"
    assert derive_applicable(sample.trial) is False


def test_study_completion_used_when_type_is_study() -> None:
    sample = _sample("S9-primary-vs-study-date")
    trial = sample.trial.model_copy(
        update={"completion_date_type": "study", "study_completion_date": date(2026, 8, 1)}
    )
    assert completion_for_clock(trial) == date(2026, 8, 1)
    trial_missing = sample.trial.model_copy(
        update={"completion_date_type": "study", "study_completion_date": None}
    )
    assert completion_for_clock(trial_missing) == sample.trial.primary_completion_date


def test_primary_completion_drives_clock() -> None:
    sample = _sample("S9-primary-vs-study-date")
    assert completion_for_clock(sample.trial) == date(2024, 9, 1)
    clock = evaluate_clock(sample.trial)
    assert clock.status == "SILENT"
    assert clock.due_date == date(2025, 9, 1)


def test_early_results_override_not_yet_due() -> None:
    sample = _sample("S20-early-results-not-yet-due")
    clock = evaluate_clock(sample.trial)
    assert clock.status == "REPORTED_REGISTRY"


def test_add_months_clips_dom() -> None:
    assert add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)


def test_derive_applicable_branches() -> None:
    sample = _sample("S11-observational-not-act")
    assert derive_applicable(sample.trial) is False
    sample = _sample("S12-device-feasibility")
    assert derive_applicable(sample.trial) is False
    sample = _sample("S16-behavioral-not-act")
    assert derive_applicable(sample.trial) is False
    sample = _sample("S19-us-site-false-still-act")
    assert derive_applicable(sample.trial) is True
    sample = _sample("S1-nct-in-abstract")
    assert derive_applicable(sample.trial) is True


def test_report_trial_combines_match_and_clock() -> None:
    sample = _sample("S1-nct-in-abstract")
    row = report_trial(sample.trial, sample.publications)
    assert row.outcome == "REPORTED_PUBLICATION"
    assert row.match.decision == "MATCH"

    sample = _sample("S15-reported-both")
    row = report_trial(sample.trial, sample.publications)
    assert row.outcome == "REPORTED_BOTH"

    sample = _sample("S5-ambiguous")
    match = match_trial(sample.trial, sample.publications)
    row = combine_outcome(sample.trial, match)
    assert row.match.decision == "AMBIGUOUS"


def test_sponsor_counts() -> None:
    rows = [report_trial(s.trial, s.publications) for s in load_samples()]
    counts = sponsor_counts(rows)
    assert "Harbor Psychiatric Consortium" in counts
    assert sum(v["n"] for v in counts.values()) == 20
    assert any(v["silent"] > 0 for v in counts.values())
