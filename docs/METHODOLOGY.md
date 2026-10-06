# Methodology (defensive)

This document states what a number from this repo is allowed to mean.

## What we claim

On a **committed, designed** probe set:

- MATCH precision and recall of an explainable three-signal matcher.
- Recall of each candidate-generation strategy on the same pairs.
- A hand-adjudicated split of unmatched trials into
  **genuinely unreported** vs **reported-but-unmatched**, with a Wilson
  95% interval on that committed set.

Those are measurements of the software against designed records. They are
not a prevalence of silent trials in any disease, sponsor, or year.

## What we do not claim

- An FDAAA 801 compliance determination.
- A sponsor ranking or league table.
- That an unmatched NCT is unreported.
- That a trial completed three or four months before the reference date
  is late.
- That journal absence is silence when the results module is posted.
- That a near-tie between two papers is a match.

## Matcher

Three signals, no learned weights: NCT-in-text, title Jaccard,
PI + condition overlap + date window. `MATCH` requires exactly one
candidate above threshold, or a lead larger than the ambiguity margin.
`AMBIGUOUS` does not pick. Features are printed individually so a
title-only fire can be seen and rejected.

## Clock

Primary completion date + 12 months. Reference date frozen at
`2026-10-06`. Registry results count as reporting. Certified delays and
good-cause extensions are **unmeasured**; until they are ingested the
clock can over-call `SILENT` on delayed ACTs.

## Unmatched is a mixture

The unmatched bucket is not a silence count. On the committed
adjudication set a substantial fraction are reported-but-unmatched
(matcher misses). Every later sponsor table must carry that band. The
Wilson interval is a bound on this designed set, not a sampling interval
over live ClinicalTrials.gov.

## Failure condition

A headline non-reporting rate is not defensible if MATCH precision is
below 0.85 or MATCH recall is below 0.80, or if unmatched is treated as
silent, or if any `NOT_YET_DUE` trial is emitted as `SILENT`.
