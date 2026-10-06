"""Deterministic string helpers for the explainable matcher."""

from __future__ import annotations

import re
import unicodedata

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOP = frozenset(
    {
        "a",
        "an",
        "and",
        "the",
        "of",
        "for",
        "in",
        "on",
        "to",
        "with",
        "vs",
        "versus",
        "study",
        "trial",
        "randomized",
        "randomised",
        "double",
        "blind",
        "placebo",
        "controlled",
        "phase",
        "patients",
        "subjects",
        "adults",
    }
)


def normalize(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return folded.lower().strip()


def tokens(text: str, *, drop_stop: bool = True) -> set[str]:
    found = set(_TOKEN_RE.findall(normalize(text)))
    if drop_stop:
        found -= _STOP
    return found


def jaccard(left: str, right: str) -> float:
    a = tokens(left)
    b = tokens(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def token_overlap(left: str, right: str) -> float:
    """Recall-like overlap: fraction of left tokens found in right."""

    a = tokens(left)
    b = tokens(right)
    if not a:
        return 0.0
    return len(a & b) / len(a)


def last_name(author: str) -> str:
    parts = [p for p in re.split(r"[\s,]+", author.strip()) if p]
    if not parts:
        return ""
    if "," in author:
        return normalize(parts[0])
    # PubMed-style "Moreau A" / "Moreau AM" — last token is initials.
    if len(parts) >= 2 and re.fullmatch(r"[A-Za-z]{1,2}\.?", parts[-1]):
        return normalize(parts[0])
    return normalize(parts[-1])
