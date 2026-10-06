# match_accuracy

## What is measured

Precision and recall of the explainable matcher (NCT-in-text, title similarity, PI + condition + date window) against 200 committed trial–publication pairing tasks.

## Why it decides something

A sponsor-level non-reporting rate is only as defensible as the linker. If MATCH precision is below 0.85 or MATCH recall is below 0.80 on this probe set, the memo says the headline statistic is not defensible.

## How to run

```bash
uv run python research/phase0/match_accuracy/run.py
```

Seed: 0. The probe set is committed under `probe_set/pairs.json` and is rebuilt by `probe_set/build.py`.

## Gold-label source

Gold decisions are designed with the records (NCT-easy, title+PI+date, ambiguous twins, true negatives, hard negatives, late reviews, hard positives). This is not a live ClinicalTrials.gov or PubMed dump. Replacing the 200 with hand-linked live pairs is the measurement that would retire that limitation.
