# unmatched_split

## What is measured

The hand-adjudicated split of 100 unmatched trials into genuinely unreported vs reported-but-unmatched.

## Why it decides something

This ratio is the largest error source for a silent-trial headline. Treating every unmatched NCT as silent overstates non-reporting by the reported-but-unmatched fraction.

## How to run

```bash
uv run python research/phase0/unmatched_split/run.py
```

## Gold-label source

Committed adjudication labels in `probe_set/labels.json`, written with the records. Not a live curator review of ClinicalTrials.gov. The labels exist so the ratio is inspectable and the matcher can be shown to miss the hidden papers.
