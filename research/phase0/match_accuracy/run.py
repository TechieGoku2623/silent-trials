"""Precision and recall of the explainable matcher on 200 labeled pairs."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from silent_trials.matcher import match_trial

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import load_json, md_table, pct, pub_from, trial_from, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
PROBE = HERE / "probe_set" / "pairs.json"
RESULTS = HERE / "results"

# Written before looking at the numbers. Headline non-reporting is defensible
# only if MATCH precision and recall both clear these floors.
PRECISION_FLOOR = 0.85
RECALL_FLOOR = 0.80


def main() -> None:
    payload = load_json(PROBE)
    pairs = payload["pairs"]
    tp = fp = fn = tn = 0
    amb_correct = 0
    amb_total = 0
    link_correct = 0
    link_total = 0
    by_cohort: dict[str, Counter[str]] = {}
    confusion = Counter()

    for row in pairs:
        trial = trial_from(row["trial"])
        pubs = [pub_from(p) for p in row["publications"]]
        pred = match_trial(trial, pubs)
        gold = str(row["gold_decision"])
        cohort = str(row["cohort"])
        gold_ids = set(row["gold_pub_ids"])
        by_cohort.setdefault(cohort, Counter())
        by_cohort[cohort][pred.decision] += 1
        confusion[f"{gold}->{pred.decision}"] += 1

        pred_match = pred.decision == "MATCH"
        gold_match = gold == "MATCH"
        if pred_match and gold_match:
            tp += 1
            link_total += 1
            if pred.chosen_pub_id in gold_ids:
                link_correct += 1
        elif pred_match and not gold_match:
            fp += 1
        elif (not pred_match) and gold_match:
            fn += 1
        else:
            tn += 1
        if gold == "AMBIGUOUS":
            amb_total += 1
            if pred.decision == "AMBIGUOUS":
                amb_correct += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    n_decision_ok = 0
    for row in pairs:
        pred_row = match_trial(trial_from(row["trial"]), [pub_from(p) for p in row["publications"]])
        if pred_row.decision == row["gold_decision"]:
            n_decision_ok += 1
    decision_acc = n_decision_ok / len(pairs)
    link_acc = link_correct / link_total if link_total else 0.0
    amb_acc = amb_correct / amb_total if amb_total else 0.0
    defensible = precision >= PRECISION_FLOOR and recall >= RECALL_FLOOR
    decision = (
        "Headline non-reporting statistic is defensible on this probe set "
        f"(MATCH precision {precision:.3f} >= {PRECISION_FLOOR:.2f} and "
        f"recall {recall:.3f} >= {RECALL_FLOOR:.2f})."
        if defensible
        else (
            "Headline non-reporting statistic is NOT defensible on this probe set. "
            f"MATCH precision {precision:.3f} (floor {PRECISION_FLOOR:.2f}) and "
            f"recall {recall:.3f} (floor {RECALL_FLOOR:.2f})."
        )
    )

    cohort_rows = []
    cohort_out = {}
    for cohort, counts in sorted(by_cohort.items()):
        n = sum(counts.values())
        cohort_out[cohort] = dict(counts)
        cohort_rows.append(
            [
                cohort,
                str(n),
                str(counts.get("MATCH", 0)),
                str(counts.get("NO_MATCH", 0)),
                str(counts.get("AMBIGUOUS", 0)),
            ]
        )

    out = {
        "n_pairs": len(pairs),
        "gold_source": payload["disclaimer"],
        "precision_floor": PRECISION_FLOOR,
        "recall_floor": RECALL_FLOOR,
        "match_tp": tp,
        "match_fp": fp,
        "match_fn": fn,
        "match_tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "decision_accuracy": decision_acc,
        "link_accuracy_given_match": link_acc,
        "ambiguous_n": amb_total,
        "ambiguous_correct": amb_correct,
        "ambiguous_accuracy": amb_acc,
        "headline_defensible": defensible,
        "decision": decision,
        "confusion": dict(confusion),
        "by_cohort": cohort_out,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / "results.json", out)
    table = md_table(
        ["metric", "value"],
        [
            ["n pairs", str(len(pairs))],
            ["MATCH precision", pct(precision)],
            ["MATCH recall", pct(recall)],
            ["MATCH F1", pct(f1)],
            ["decision accuracy", pct(decision_acc)],
            ["link accuracy | pred MATCH", pct(link_acc)],
            ["AMBIGUOUS accuracy", pct(amb_acc)],
            ["headline defensible", "yes" if defensible else "no"],
        ],
    )
    cohort_table = md_table(["cohort", "n", "MATCH", "NO_MATCH", "AMBIGUOUS"], cohort_rows)
    md = (
        "# match_accuracy results\n\n"
        f"n = {len(pairs)} committed trial–publication pairing tasks.\n\n"
        f"{decision}\n\n"
        f"{table}\n\n"
        f"{cohort_table}\n"
    )
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
