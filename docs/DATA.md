# Data

Phase 0 does not download ClinicalTrials.gov, AACT, or PubMed. The committed
objects are:

- `data/sample/samples.json` — 20 designed demo cases (see
  `data/sample/README.md`)
- `research/phase0/match_accuracy/probe_set/pairs.json` — 200 designed
  trial–publication pairing tasks
- `research/phase0/unmatched_split/probe_set/labels.json` — 100
  hand-adjudicated unmatched-trial labels

No patient-identifiable data. No restricted-access corpus. License notes for
the production sources (ClinicalTrials.gov / AACT, PubMed, FDAAA
TrialsTracker) are in `docs/phase-0/research-memo.md` §3.

Full-database redistribution is out of scope. Ingest in later phases writes a
manifest (source URL, retrieval timestamp, row count, sha256) and keeps raw
files in gitignored bronze storage.

The reference date for every clock calculation is **2026-10-06**. Changing it
changes NOT_YET_DUE vs SILENT for recent completions.
