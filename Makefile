export PATH := $(HOME)/.local/bin:$(PATH)
UV ?= uv

.PHONY: setup lint test research eval demo record report

setup:
	$(UV) sync --extra dev

lint:
	$(UV) run ruff check src tests research scripts
	$(UV) run ruff format --check src tests research scripts
	$(UV) run mypy

test:
	$(UV) run pytest

research:
	$(UV) run python research/phase0/run_all.py

eval:
	$(UV) run python research/phase0/match_accuracy/run.py
	$(UV) run python research/phase0/candidate_recall/run.py
	$(UV) run python research/phase0/unmatched_split/run.py
	$(UV) run python research/phase0/render_docs.py

demo:
	$(UV) run silent-trials demo

record:
	$(UV) run python scripts/record_demo.py

report:
	$(UV) run silent-trials report --out docs/dashboard.html
