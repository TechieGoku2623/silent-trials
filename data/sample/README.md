# Sample cases

These 20 records are designed, not sampled. Each one exists to exercise a
path the walkthrough names. NCT identifiers, dates, and abstracts are
committed stand-ins so `make demo` and `make test` run with no network.

This directory contains no patient-identifiable data. Identifiers are
synthetic (`NCT00000001`–`NCT00000020`). This is not a ClinicalTrials.gov
dump.

| ID | NCT | Why it is here |
| --- | --- | --- |
| S1 | NCT00000001 | Easy match: the abstract cites the NCT. |
| S2 | NCT00000002 | No NCT; match on title, PI, condition, date window. |
| S3 | NCT00000003 | Completed 4 months before 2026-10-06. NOT_YET_DUE, not delinquent. |
| S4 | NCT00000004 | Completed 3 years ago, results posted, never journal-published. REPORTED via registry. |
| S5 | NCT00000005 | Two plausible publications. Matcher returns AMBIGUOUS and does not pick. |
| S6 | NCT00000006 | True silent: applicable, past due, nothing posted. |
| S7 | NCT00000007 | Phase 1 drug trial. NOT_APPLICABLE. |
| S8 | NCT00000008 | Past due, journal article with NCT, empty results module. REPORTED_PUBLICATION. |
| S9 | NCT00000009 | Primary vs study completion. Clock uses primary. |
| S10 | NCT00000010 | Completed 3 months ago. Still NOT_YET_DUE. |
| S11 | NCT00000011 | Observational ALS cohort. NOT_APPLICABLE. |
| S12 | NCT00000012 | Device feasibility. NOT_APPLICABLE. |
| S13 | NCT00000013 | Similar title, wrong PI and condition. Must not match. |
| S14 | NCT00000014 | Same PI, review eight years later. Outside the date window. |
| S15 | NCT00000015 | Registry results and a journal article. REPORTED_BOTH. |
| S16 | NCT00000016 | Behavioral intervention. NOT_APPLICABLE. |
| S17 | NCT00000017 | Second Harbor silent trial for the sponsor-tally path. |
| S18 | NCT00000018 | Empty corpus. Genuinely unreported, not a matcher miss. |
| S19 | NCT00000019 | No US site, FDA-regulated product. Still applicable, then SILENT. |
| S20 | NCT00000020 | Results posted before the deadline. REPORTED_REGISTRY, not NOT_YET_DUE. |

S3 and S10 are the teaching cases for the time-aware clock. A demo that
only shows S1 and S6 teaches nothing about when not to call a trial silent.

S4 is the case a journal-only definition gets wrong.

S5 is the case a greedy linker gets confidently wrong.

LLM / API response cache is not applicable. Phase 0 does not call a model
or a live registry.
