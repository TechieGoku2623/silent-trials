"""Candidate-generation strategies measured separately in Phase 0."""

from __future__ import annotations

from collections.abc import Callable

from silent_trials.matcher import (
    condition_overlap,
    date_in_window,
    nct_in_text,
    pi_in_authors,
    score_pair,
)
from silent_trials.schemas import PublicationRecord, TrialRecord
from silent_trials.text import jaccard

StrategyFn = Callable[[TrialRecord, list[PublicationRecord]], list[str]]

TITLE_RECALL_THRESHOLD = 0.34
CONDITION_RECALL_MIN = 0.34


def strategy_nct_id(trial: TrialRecord, publications: list[PublicationRecord]) -> list[str]:
    return [pub.pub_id for pub in publications if nct_in_text(trial.nct_id, pub)]


def strategy_title(trial: TrialRecord, publications: list[PublicationRecord]) -> list[str]:
    return [
        pub.pub_id
        for pub in publications
        if jaccard(trial.title, pub.title) >= TITLE_RECALL_THRESHOLD
    ]


def strategy_pi_condition_date(
    trial: TrialRecord, publications: list[PublicationRecord]
) -> list[str]:
    out: list[str] = []
    for pub in publications:
        if (
            pi_in_authors(trial, pub)
            and condition_overlap(trial, pub) >= CONDITION_RECALL_MIN
            and date_in_window(trial, pub)
        ):
            out.append(pub.pub_id)
    return out


def strategy_combined(trial: TrialRecord, publications: list[PublicationRecord]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for fn in (strategy_nct_id, strategy_title, strategy_pi_condition_date):
        for pub_id in fn(trial, publications):
            if pub_id not in seen:
                seen.add(pub_id)
                ordered.append(pub_id)
    return ordered


STRATEGIES: dict[str, StrategyFn] = {
    "nct_id_search": strategy_nct_id,
    "title_search": strategy_title,
    "pi_condition_date": strategy_pi_condition_date,
    "combined": strategy_combined,
}


def generate_candidates(
    trial: TrialRecord,
    publications: list[PublicationRecord],
    strategy: str,
) -> list[str]:
    if strategy not in STRATEGIES:
        raise KeyError(f"unknown strategy: {strategy}")
    return STRATEGIES[strategy](trial, publications)


def ranked_corpus(trial: TrialRecord, publications: list[PublicationRecord]) -> list[str]:
    """Score the whole corpus; used only as a diagnostic, not a strategy."""

    scored = [score_pair(trial, pub) for pub in publications]
    scored.sort(key=lambda row: (-row.score, row.pub_id))
    return [row.pub_id for row in scored if row.score > 0.0]
