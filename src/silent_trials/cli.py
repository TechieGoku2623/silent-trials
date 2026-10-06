"""CLI: explainable match, time-aware clock, sample dashboard."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from silent_trials import REFERENCE_DATE_ISO, SAFETY_DISCLAIMER, __version__
from silent_trials.catalog import load_samples, sample_by_nct
from silent_trials.config import get_settings
from silent_trials.dashboard import write_dashboard
from silent_trials.fdaaa import REFERENCE_DATE, evaluate_clock
from silent_trials.logging import configure_logging
from silent_trials.matcher import match_trial
from silent_trials.schemas import CandidateScore, FdaaaClock, MatchResult, SampleCase

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console(width=140)

ROUTE_LABEL = {
    "REPORTED_REGISTRY": "registry results module",
    "REPORTED_PUBLICATION": "matched journal publication",
    "REPORTED_BOTH": "registry results and matched publication",
}
REPORTED_STATUSES = frozenset(ROUTE_LABEL)
DEFAULT_DASHBOARD = Path("docs/dashboard.html")


def _yn(flag: bool) -> str:
    return "yes" if flag else "no"


def _print_disclaimer() -> None:
    console.print()
    console.print(SAFETY_DISCLAIMER)


def _print_candidate(score: CandidateScore, *, indent: str = "  ") -> None:
    console.print(f"{indent}{score.pub_id}  score={score.score:.3f}  confidence={score.score:.3f}")
    console.print(f"{indent}  nct_in_text:        {_yn(score.nct_in_text)}")
    console.print(f"{indent}  title_similarity:   {score.title_similarity:.3f}")
    console.print(f"{indent}  pi_match:           {_yn(score.pi_match)}")
    console.print(f"{indent}  condition_overlap:  {score.condition_overlap:.3f}")
    console.print(f"{indent}  date_in_window:     {_yn(score.date_in_window)}")
    reasons = "; ".join(score.reasons) if score.reasons else "(no firing signal)"
    console.print(f"{indent}  reasons:            {reasons}")


def _print_match(sample: SampleCase, result: MatchResult, *, explain: bool) -> None:
    console.print(f"[bold]{sample.nct_id}[/bold]  {sample.sample_id}")
    console.print(f"decision:   {result.decision}")
    if result.decision == "AMBIGUOUS":
        console.print("chosen:     (none — matcher does not pick)")
    elif result.chosen_pub_id:
        console.print(f"chosen:     {result.chosen_pub_id}")
    else:
        console.print("chosen:     (none)")
    console.print(f"rationale:  {result.rationale}")
    if explain:
        console.print()
        console.print("candidates (all scored; features shown individually):")
        if not result.candidates:
            console.print("  (empty corpus — no candidates)")
        for row in result.candidates:
            _print_candidate(row)
        if result.decision == "AMBIGUOUS":
            above = [c for c in result.candidates if c.score >= 0.50]
            console.print()
            console.print(
                f"AMBIGUOUS: {len(above)} candidates clear the 0.50 threshold "
                "and sit inside the margin. Matcher does not pick."
            )


def _headline_status(clock: FdaaaClock) -> str:
    if clock.status in REPORTED_STATUSES:
        return "REPORTED"
    return clock.status


def _print_status(sample: SampleCase, clock: FdaaaClock) -> None:
    headline = _headline_status(clock)
    console.print(f"[bold]{sample.nct_id}[/bold]  {sample.sample_id}")
    console.print(f"status:          {headline}")
    if clock.status in REPORTED_STATUSES:
        console.print(f"posting route:   {ROUTE_LABEL[clock.status]} ({clock.status})")
        posted = sample.trial.registry_results_first_posted
        if posted is not None:
            console.print(f"registry posted: {posted.isoformat()}")
    console.print(f"clock status:    {clock.status}")
    console.print(f"reference date:  {clock.reference_date.isoformat()}")
    console.print(
        f"completion:      {clock.completion_date.isoformat()} ({clock.completion_date_type})"
    )
    if clock.due_date is not None:
        console.print(f"due date:        {clock.due_date.isoformat()}")
    if clock.days_remaining is not None:
        console.print(f"days remaining:  {clock.days_remaining}")
    console.print(f"days elapsed:    {clock.days_elapsed}")
    console.print(f"applicable:      {_yn(clock.applicable)}")
    console.print(f"rationale:       {clock.rationale}")


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
    _print_disclaimer()
    if dry_run:
        console.print(
            "\nDry run only. Run `silent-trials demo` or `make demo` for the "
            "full match/status walkthrough on the designed catalog."
        )
    console.print(f"Sample manifest: {get_settings().sample_dir / 'samples.json'}")


@app.command("sample-path")
def sample_path() -> None:
    """Print the committed sample directory path."""

    console.print(str(get_settings().sample_dir.resolve()))


@app.command("match")
def match_cmd(
    nct: str = typer.Option(..., "--nct", help="NCT identifier from the sample catalog"),
    explain: bool = typer.Option(False, "--explain", help="Print every candidate and feature"),
) -> None:
    """Score publications for one catalog trial. Does not pick on a near-tie."""

    try:
        sample = sample_by_nct(nct)
    except KeyError as exc:
        console.print(str(exc))
        raise typer.Exit(code=2) from exc
    result = match_trial(sample.trial, sample.publications)
    _print_match(sample, result, explain=explain)
    _print_disclaimer()


@app.command("status")
def status_cmd(
    nct: str = typer.Option(..., "--nct", help="NCT identifier from the sample catalog"),
) -> None:
    """Print the FDAAA clock. REPORTED names the posting route."""

    try:
        sample = sample_by_nct(nct)
    except KeyError as exc:
        console.print(str(exc))
        raise typer.Exit(code=2) from exc
    match = match_trial(sample.trial, sample.publications)
    clock = evaluate_clock(
        sample.trial,
        reference=REFERENCE_DATE,
        matched_publication=match.decision == "MATCH",
    )
    _print_status(sample, clock)
    if match.decision != "NO_MATCH":
        console.print(f"matcher:         {match.decision} chosen={match.chosen_pub_id}")
    _print_disclaimer()


@app.command("report")
def report_cmd(
    out: Path = typer.Option(
        DEFAULT_DASHBOARD,
        "--out",
        help="HTML path, relative to the repo root unless absolute",
    ),
) -> None:
    """Write a static HTML dashboard from the sample catalog. No credentials."""

    path = out if out.is_absolute() else get_settings().repo_root / out
    write_dashboard(path)
    console.print(f"wrote {path}")
    _print_disclaimer()


@app.command("demo")
def demo_cmd() -> None:
    """Full walkthrough: NCT match, no-NCT features, ambiguity, clock."""

    console.print("[bold]silent-trials walkthrough[/bold]")
    console.print(f"Reference date {REFERENCE_DATE_ISO}. Designed catalog only.\n")

    console.print("[bold]Step 1 — NCT-in-abstract match[/bold]")
    sample = sample_by_nct("NCT00000001")
    _print_match(sample, match_trial(sample.trial, sample.publications), explain=True)
    console.print()

    console.print("[bold]Step 2 — no NCT; title / PI / condition / date[/bold]")
    sample = sample_by_nct("NCT00000002")
    result = match_trial(sample.trial, sample.publications)
    _print_match(sample, result, explain=True)
    if result.candidates:
        scored = result.candidates[0]
        console.print()
        console.print("features shown individually (no NCT signal):")
        console.print(f"  nct_in_text:       {_yn(scored.nct_in_text)}")
        console.print(f"  title_similarity:  {scored.title_similarity:.3f}")
        console.print(f"  pi_match:          {_yn(scored.pi_match)}")
        console.print(f"  condition_overlap: {scored.condition_overlap:.3f}")
        console.print(f"  date_in_window:    {_yn(scored.date_in_window)}")
    console.print()

    console.print("[bold]Step 3 — AMBIGUOUS; matcher does not pick[/bold]")
    sample = sample_by_nct("NCT00000005")
    _print_match(sample, match_trial(sample.trial, sample.publications), explain=True)
    console.print()

    console.print("[bold]Step 4 — clock: NOT_YET_DUE[/bold]")
    sample = sample_by_nct("NCT00000003")
    clock = evaluate_clock(sample.trial, reference=REFERENCE_DATE)
    _print_status(sample, clock)
    console.print()

    console.print("[bold]Step 5 — clock: REPORTED via registry[/bold]")
    sample = sample_by_nct("NCT00000004")
    clock = evaluate_clock(sample.trial, reference=REFERENCE_DATE)
    _print_status(sample, clock)
    _print_disclaimer()


def repo_root() -> Path:
    return get_settings().repo_root


if __name__ == "__main__":
    app()
