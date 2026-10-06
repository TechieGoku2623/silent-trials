"""Hand-adjudicated split of 100 unmatched trials.

The ratio genuinely-unreported vs reported-but-unmatched is the largest
error source for a sponsor-level silence rate. Labels are committed.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from silent_trials.matcher import match_trial

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import load_json, md_table, pct, pub_from, trial_from, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
PROBE = HERE / "probe_set" / "labels.json"
RESULTS = HERE / "results"


def main() -> None:
    payload = load_json(PROBE)
    records = payload["records"]
    labels = Counter(str(row["label"]) for row in records)
    n = len(records)
    genuine = labels.get("genuinely_unreported", 0)
    missed = labels.get("reported_but_unmatched", 0)
    genuine_frac = genuine / n
    missed_frac = missed / n

    matcher_nomatch = 0
    matcher_other = 0
    for row in records:
        pred = match_trial(trial_from(row["trial"]), [pub_from(p) for p in row["publications"]])
        if pred.decision == "NO_MATCH":
            matcher_nomatch += 1
        else:
            matcher_other += 1

    decision = (
        f"{missed}/{n} = {missed_frac:.3f} of unmatched trials are "
        "reported-but-unmatched. Treating unmatched as silent overstates "
        "non-reporting by that fraction on this adjudication set. "
        f"{genuine}/{n} = {genuine_frac:.3f} are genuinely unreported."
    )
    out = {
        "n": n,
        "genuinely_unreported": genuine,
        "reported_but_unmatched": missed,
        "genuinely_unreported_fraction": genuine_frac,
        "reported_but_unmatched_fraction": missed_frac,
        "overstatement_if_unmatched_equals_silent": missed_frac,
        "matcher_no_match": matcher_nomatch,
        "matcher_not_no_match": matcher_other,
        "decision": decision,
        "gold_source": payload["disclaimer"],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", out)
    table = md_table(
        ["label", "n", "fraction"],
        [
            ["genuinely_unreported", str(genuine), pct(genuine_frac)],
            ["reported_but_unmatched", str(missed), pct(missed_frac)],
        ],
    )
    md = (
        "# unmatched_split results\n\n"
        f"n = {n} hand-adjudicated unmatched trials.\n\n"
        f"{decision}\n\n"
        f"{table}\n\n"
        f"Matcher emitted NO_MATCH on {matcher_nomatch}/{n} of these records "
        f"({matcher_other} were not NO_MATCH).\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
