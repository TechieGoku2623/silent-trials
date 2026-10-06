# Architecture and data contracts

Phase 1 freeze of the objects the CLI, the matcher, and the clock share.
Nothing here is a live ClinicalTrials.gov or PubMed ingest.

## Topology

```
TrialRecord + PublicationRecord[]
        │
        ├─► candidate strategies (NCT / title / PI+condition+date / union)
        ├─► score_pair → CandidateScore[] → match_trial → MatchResult
        └─► evaluate_clock → FdaaaClock
                │
                └─► combine_outcome → ReportingOutcome
```

`AMBIGUOUS` is a first-class decision. Two candidates that both clear the
score threshold and sit inside the margin do not produce a pick.

`NOT_YET_DUE` is a first-class clock status. A trial whose primary
completion plus 12 months is still after the reference date is not silent.

## Contracts

| Object | Module | Role |
| --- | --- | --- |
| `TrialRecord` | `schemas.py` | One registered trial. ACT flag is committed, not inferred at score time. |
| `PublicationRecord` | `schemas.py` | One candidate paper. NCT may be absent. |
| `CandidateScore` | `schemas.py` | Per-pair features: NCT-in-text, title Jaccard, PI, condition overlap, date window, score, reasons. |
| `MatchResult` | `schemas.py` | `MATCH` / `NO_MATCH` / `AMBIGUOUS` plus every scored candidate. |
| `FdaaaClock` | `schemas.py` | Time-aware 12-month clock. Reference date `2026-10-06`. |
| `ReportingOutcome` | `schemas.py` | Clock + match. Used for sample tallies, not a sponsor ranking. |
| `SampleCase` | `schemas.py` | One designed demo row in `data/sample/samples.json`. |

## CLI surface (Phase 2)

| Command | Contract |
| --- | --- |
| `silent-trials match --nct --explain` | Score the catalog publications for that NCT. Print every candidate and every feature. Do not hide a near-tie. |
| `silent-trials status --nct` | Print the clock. Headline `REPORTED` names the posting route. `NOT_YET_DUE` prints days remaining. |
| `silent-trials report` | Write static HTML from the sample catalog. Optional. No credentials. |
| `silent-trials demo` | Full walkthrough of the designed paths. |

## What is not in this slice

Live AACT / PubMed ingest, certified-delay fields, a learned linker, and a
hosted API. Those remain later work. The matcher and clock already exist;
this slice only exposes them.
