from __future__ import annotations

from datetime import date

from silent_trials.candidates import (
    generate_candidates,
    ranked_corpus,
    strategy_combined,
    strategy_nct_id,
    strategy_pi_condition_date,
    strategy_title,
)
from silent_trials.cli import load_samples
from silent_trials.matcher import match_trial, nct_in_text, score_pair
from silent_trials.schemas import PublicationRecord, TrialRecord
from silent_trials.text import jaccard, last_name, normalize, token_overlap, tokens


def _sample(sample_id: str):
    return next(s for s in load_samples() if s.sample_id == sample_id)


def test_nct_in_abstract_matches() -> None:
    sample = _sample("S1-nct-in-abstract")
    result = match_trial(sample.trial, sample.publications)
    assert result.decision == "MATCH"
    assert result.chosen_pub_id == "pub-s1"
    assert nct_in_text(sample.trial.nct_id, sample.publications[0])


def test_title_pi_condition_date_matches_without_nct() -> None:
    sample = _sample("S2-title-pi-condition-date")
    result = match_trial(sample.trial, sample.publications)
    assert result.decision == "MATCH"
    assert result.chosen_pub_id == "pub-s2"
    scored = score_pair(sample.trial, sample.publications[0])
    assert scored.nct_in_text is False
    assert scored.pi_match is True
    assert scored.date_in_window is True


def test_two_plausible_candidates_are_ambiguous() -> None:
    sample = _sample("S5-ambiguous")
    result = match_trial(sample.trial, sample.publications)
    assert result.decision == "AMBIGUOUS"
    assert result.chosen_pub_id is None
    assert "does not pick" in result.rationale


def test_hard_negative_does_not_match() -> None:
    sample = _sample("S13-hard-negative-title")
    result = match_trial(sample.trial, sample.publications)
    assert result.decision == "NO_MATCH"


def test_outside_date_window_does_not_match() -> None:
    sample = _sample("S14-outside-date-window")
    result = match_trial(sample.trial, sample.publications)
    assert result.decision == "NO_MATCH"


def test_empty_corpus_is_no_match() -> None:
    sample = _sample("S18-empty-corpus-unreported")
    result = match_trial(sample.trial, sample.publications)
    assert result.decision == "NO_MATCH"


def test_clear_winner_among_two() -> None:
    sample = _sample("S1-nct-in-abstract")
    weak = PublicationRecord(
        pub_id="pub-weak",
        title="Unrelated nutrition study",
        abstract="Vitamin D in older adults.",
        authors=["Nguyen T"],
        journal="x",
        published=date(2024, 1, 1),
        mesh_terms=["Vitamin D"],
    )
    result = match_trial(sample.trial, [sample.publications[0], weak])
    assert result.decision == "MATCH"
    assert result.chosen_pub_id == "pub-s1"


def test_candidate_strategies() -> None:
    sample = _sample("S1-nct-in-abstract")
    pubs = sample.publications
    assert strategy_nct_id(sample.trial, pubs) == ["pub-s1"]
    sample2 = _sample("S2-title-pi-condition-date")
    assert sample2.publications[0].pub_id in strategy_title(sample2.trial, sample2.publications)
    assert sample2.publications[0].pub_id in strategy_pi_condition_date(
        sample2.trial, sample2.publications
    )
    assert sample2.publications[0].pub_id in strategy_combined(sample2.trial, sample2.publications)
    assert generate_candidates(sample.trial, pubs, "nct_id_search") == ["pub-s1"]
    ranked = ranked_corpus(sample.trial, pubs)
    assert "pub-s1" in ranked


def test_unknown_strategy_raises() -> None:
    sample = _sample("S1-nct-in-abstract")
    try:
        generate_candidates(sample.trial, sample.publications, "not-a-strategy")
    except KeyError as exc:
        assert "unknown strategy" in str(exc)
    else:
        raise AssertionError("expected KeyError")


def test_text_helpers() -> None:
    assert normalize(" naïve ") == "naive"
    assert "depression" in tokens("Major Depression Trial")
    assert jaccard("sertraline for depression", "sertraline for depression") == 1.0
    assert jaccard("", "") == 1.0
    assert jaccard("abc", "") == 0.0
    assert token_overlap("major depressive disorder", "adults with major depressive disorder") > 0.9
    assert token_overlap("", "x") == 0.0
    assert last_name("Moreau, Alex") == "moreau"
    assert last_name("Alex Moreau") == "moreau"
    assert last_name("Moreau A") == "moreau"
    assert last_name("Moreau AM") == "moreau"
    assert last_name("   ") == ""


def test_trial_record_roundtrip() -> None:
    sample = _sample("S4-registry-only")
    raw = sample.trial.model_dump(mode="json")
    assert TrialRecord.model_validate(raw).nct_id == "NCT00000004"
