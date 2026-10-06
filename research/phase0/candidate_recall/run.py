"""Recall per candidate-generation strategy on the same 200 pairs."""

from __future__ import annotations

import sys
from pathlib import Path

from silent_trials.candidates import STRATEGIES, generate_candidates

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import load_json, md_table, pct, pub_from, trial_from, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
PROBE = HERE.parent / "match_accuracy" / "probe_set" / "pairs.json"
RESULTS = HERE / "results"


def main() -> None:
    payload = load_json(PROBE)
    pairs = payload["pairs"]
    # Shared corpus: every publication attached to any pair, plus the pair's own list.
    corpus_map: dict[str, dict[str, object]] = {}
    for row in pairs:
        for raw in row["publications"]:
            corpus_map[str(raw["pub_id"])] = raw
    corpus = [pub_from(raw) for raw in corpus_map.values()]

    positives = [row for row in pairs if row["gold_pub_ids"]]
    per_strategy: dict[str, dict[str, float | int]] = {}
    rows_md: list[list[str]] = []
    for name in STRATEGIES:
        retrieved = 0
        gold_n = 0
        for row in positives:
            trial = trial_from(row["trial"])
            gold = set(row["gold_pub_ids"])
            gold_n += len(gold)
            found = set(generate_candidates(trial, corpus, name))
            retrieved += len(gold & found)
        recall = retrieved / gold_n if gold_n else 0.0
        per_strategy[name] = {
            "gold_publications": gold_n,
            "retrieved": retrieved,
            "recall": recall,
            "n_positive_trials": len(positives),
        }
        rows_md.append([name, str(len(positives)), str(gold_n), str(retrieved), pct(recall)])

    combined_recall = float(per_strategy["combined"]["recall"])
    nct_recall = float(per_strategy["nct_id_search"]["recall"])
    decision = (
        f"NCT search recall is {nct_recall:.3f} because most gold papers in this "
        f"probe set do not print an NCT. Combined-strategy recall is "
        f"{combined_recall:.3f}. Title and PI+condition+date are not optional "
        "if the matcher is going to see the typical psychiatry paper."
    )
    out = {
        "n_pairs": len(pairs),
        "n_positive_trials": len(positives),
        "corpus_size": len(corpus),
        "strategies": per_strategy,
        "decision": decision,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", out)
    table = md_table(
        ["strategy", "positive trials", "gold pubs", "retrieved", "recall"],
        rows_md,
    )
    md = (
        "# candidate_recall results\n\n"
        f"Same 200 pairing tasks. Shared corpus size = {len(corpus)}.\n\n"
        f"{decision}\n\n"
        f"{table}\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
