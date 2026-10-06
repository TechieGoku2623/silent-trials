"""Explainable trial–publication matcher.

Three signals, no learned weights:

1. NCT identifier present in the publication title, abstract, or body.
2. Title token Jaccard similarity.
3. Principal-investigator last name + condition overlap + date window
   around the primary completion date.

The matcher returns MATCH only when exactly one candidate clears the score
threshold (or one candidate dominates the rest). Two plausible candidates
return AMBIGUOUS and do not pick. This is intentional: a silent-trial
headline that force-picks among near-ties is not defensible.
"""

from __future__ import annotations

import re
from datetime import date

from silent_trials.fdaaa import add_months
from silent_trials.schemas import (
    CandidateScore,
    MatchResult,
    PublicationRecord,
    TrialRecord,
)
from silent_trials.text import jaccard, last_name, normalize, token_overlap

NCT_RE = re.compile(r"NCT\d{8}", re.IGNORECASE)
TITLE_WEIGHT = 0.45
PI_CONDITION_DATE_WEIGHT = 0.55
NCT_WEIGHT = 1.0
SCORE_THRESHOLD = 0.50
AMBIGUOUS_MARGIN = 0.22
DATE_WINDOW_MONTHS_BEFORE = 6
DATE_WINDOW_MONTHS_AFTER = 36
CONDITION_OVERLAP_MIN = 0.34


def publication_text(pub: PublicationRecord) -> str:
    return " ".join([pub.title, pub.abstract, pub.body])


def nct_in_text(nct_id: str, pub: PublicationRecord) -> bool:
    blob = publication_text(pub)
    found = {m.group(0).upper() for m in NCT_RE.finditer(blob)}
    return nct_id.upper() in found


def pi_in_authors(trial: TrialRecord, pub: PublicationRecord) -> bool:
    target = normalize(trial.pi_last)
    if not target:
        return False
    names = [last_name(a) for a in pub.authors]
    if target in names:
        return True
    return any(target == normalize(a) for a in pub.authors)


def condition_overlap(trial: TrialRecord, pub: PublicationRecord) -> float:
    haystack = " ".join([pub.title, pub.abstract, " ".join(pub.mesh_terms)])
    return max(token_overlap(trial.condition, haystack), jaccard(trial.condition, haystack))


def date_in_window(trial: TrialRecord, pub: PublicationRecord) -> bool:
    start = add_months(trial.primary_completion_date, -DATE_WINDOW_MONTHS_BEFORE)
    end = add_months(trial.primary_completion_date, DATE_WINDOW_MONTHS_AFTER)
    return start <= pub.published <= end


def score_pair(trial: TrialRecord, pub: PublicationRecord) -> CandidateScore:
    nct = nct_in_text(trial.nct_id, pub)
    title_sim = jaccard(trial.title, pub.title)
    pi = pi_in_authors(trial, pub)
    cond = condition_overlap(trial, pub)
    window = date_in_window(trial, pub)
    reasons: list[str] = []
    score = 0.0
    if nct:
        score += NCT_WEIGHT
        reasons.append(f"nct_in_text:{trial.nct_id}")
    if title_sim >= 0.40:
        score += TITLE_WEIGHT * title_sim
        reasons.append(f"title_similarity={title_sim:.2f}")
    elif title_sim >= 0.22:
        score += 0.20 * title_sim
        reasons.append(f"weak_title_similarity={title_sim:.2f}")
    if pi and cond >= CONDITION_OVERLAP_MIN and window:
        score += PI_CONDITION_DATE_WEIGHT
        reasons.append("pi_condition_date")
    else:
        bits: list[str] = []
        if pi:
            bits.append("pi")
        if cond >= CONDITION_OVERLAP_MIN:
            bits.append(f"condition={cond:.2f}")
        if window:
            bits.append("date_window")
        if len(bits) == 2:
            score += 0.18
            reasons.append("partial:" + "+".join(bits))
        elif bits:
            reasons.append("partial:" + "+".join(bits))
    return CandidateScore(
        pub_id=pub.pub_id,
        score=round(score, 4),
        reasons=reasons,
        nct_in_text=nct,
        title_similarity=round(title_sim, 4),
        pi_match=pi,
        condition_overlap=round(cond, 4),
        date_in_window=window,
    )


def match_trial(
    trial: TrialRecord,
    publications: list[PublicationRecord],
    *,
    as_of: date | None = None,
) -> MatchResult:
    """Score every publication and decide MATCH / NO_MATCH / AMBIGUOUS."""

    del as_of  # reserved so later phases can freeze a PubMed snapshot date
    scored = [score_pair(trial, pub) for pub in publications]
    scored.sort(key=lambda row: (-row.score, row.pub_id))
    above = [row for row in scored if row.score >= SCORE_THRESHOLD]
    if not above:
        return MatchResult(
            nct_id=trial.nct_id,
            decision="NO_MATCH",
            chosen_pub_id=None,
            candidates=scored,
            rationale="No candidate reached the 0.50 score threshold.",
        )
    if len(above) == 1:
        winner = above[0]
        return MatchResult(
            nct_id=trial.nct_id,
            decision="MATCH",
            chosen_pub_id=winner.pub_id,
            candidates=scored,
            rationale=f"Single candidate {winner.pub_id} scored {winner.score:.2f}: "
            + "; ".join(winner.reasons),
        )
    top, second = above[0], above[1]
    if (top.score - second.score) < AMBIGUOUS_MARGIN:
        return MatchResult(
            nct_id=trial.nct_id,
            decision="AMBIGUOUS",
            chosen_pub_id=None,
            candidates=scored,
            rationale=(
                f"{top.pub_id} ({top.score:.2f}) and {second.pub_id} "
                f"({second.score:.2f}) both clear the threshold and are "
                f"within {AMBIGUOUS_MARGIN:.2f}; matcher does not pick."
            ),
        )
    return MatchResult(
        nct_id=trial.nct_id,
        decision="MATCH",
        chosen_pub_id=top.pub_id,
        candidates=scored,
        rationale=(
            f"{top.pub_id} scored {top.score:.2f} and leads {second.pub_id} "
            f"({second.score:.2f}) by more than {AMBIGUOUS_MARGIN:.2f}."
        ),
    )
