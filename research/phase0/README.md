# Phase 0 harnesses

`make research` runs these in order:

1. `data/sample/build.py` — rebuild the 20 designed demo cases
2. `match_accuracy/probe_set/build.py` — rebuild the committed 200 pairing tasks
3. `unmatched_split/probe_set/build.py` — rebuild the 100 adjudication labels
4. `match_accuracy/run.py` — matcher precision / recall
5. `candidate_recall/run.py` — recall per candidate-generation strategy on the same 200
6. `unmatched_split/run.py` — genuinely unreported vs reported-but-unmatched
7. `render_docs.py` — write `docs/phase-0/research-memo.md`, `docs/EVALUATION.md`, and the measured tables in `README.md`

No number in the memo is typed by hand. If a quantity cannot be produced here, the memo says **unmeasured** and names the measurement that would settle it.
