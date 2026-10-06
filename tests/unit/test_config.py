from __future__ import annotations

import os

from silent_trials.cli import repo_root
from silent_trials.config import get_settings
from silent_trials.logging import configure_logging


def test_settings_point_at_committed_sample_dir() -> None:
    settings = get_settings()
    assert (settings.sample_dir / "README.md").is_file()
    assert (settings.research_dir / "run_all.py").is_file()
    assert repo_root() == settings.repo_root


def test_configure_logging_does_not_raise() -> None:
    configure_logging()
    os.environ["SILENT_TRIALS_ENV"] = "prod"
    try:
        configure_logging()
    finally:
        os.environ.pop("SILENT_TRIALS_ENV", None)
