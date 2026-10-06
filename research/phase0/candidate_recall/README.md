# candidate_recall

## What is measured

Recall of each candidate-generation strategy — NCT search, title search, PI+condition+date, and their union — against the gold publications in the same 200 pairing tasks, searched over the shared committed corpus.

## Why it decides something

If NCT search is the only generator, most psychiatry papers that omit the identifier never reach the matcher. This measurement decides whether title and PI+condition+date generators are mandatory.

## How to run

```bash
uv run python research/phase0/candidate_recall/run.py
```

Uses `../match_accuracy/probe_set/pairs.json`. No separate gold file.
