"""Phase 0 CLI. Reconciliation, sponsor tables, and APIs are Phase 2."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from silent_trials import SAFETY_DISCLAIMER, __version__
from silent_trials.config import get_settings
from silent_trials.logging import configure_logging
from silent_trials.schemas import SampleCase

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console(width=140)


def load_samples() -> list[SampleCase]:
    path = get_settings().sample_dir / "samples.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [SampleCase.model_validate(item) for item in raw["samples"]]


@app.callback()
def _main() -> None:
    configure_logging()


@app.command("version")
def version() -> None:
    """Print the package version."""

    console.print(f"silent-trials {__version__}")


@app.command("demo-plan")
def demo_plan(
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run"),
) -> None:
    """Print the designed sample cases and the path each exercises."""

    samples = load_samples()
    console.print("[bold]silent-trials designed sample cases[/bold]\n")
    for sample in samples:
        console.print(f"[bold]{sample.sample_id}[/bold]  {sample.nct_id}")
        console.print(f"  path:     {sample.path_exercised}")
        console.print(f"  expected: {sample.expected_behavior}\n")
    console.print()
    console.print(SAFETY_DISCLAIMER)
    if dry_run:
        console.print(
            "\nDry run only. Reconciliation (`silent-trials reconcile`) is "
            "Phase 2; this command exists so `make demo` can show that the "
            "sample set is designed, not sampled from a live registry dump."
        )
    console.print(f"Sample manifest: {get_settings().sample_dir / 'samples.json'}")


@app.command("sample-path")
def sample_path() -> None:
    """Print the committed sample directory path."""

    console.print(str(get_settings().sample_dir.resolve()))


def repo_root() -> Path:
    return get_settings().repo_root
