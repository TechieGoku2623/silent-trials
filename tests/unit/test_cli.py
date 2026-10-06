from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from silent_trials.cli import app, load_samples
from silent_trials.dashboard import render_dashboard_html, write_dashboard

runner = CliRunner()


def test_demo_plan_lists_named_paths() -> None:
    result = runner.invoke(app, ["demo-plan"])
    assert result.exit_code == 0, result.stdout
    assert "S1-nct-in-abstract" in result.stdout
    assert "NCT00000001" in result.stdout
    assert "S3-not-yet-due" in result.stdout
    assert "S4-registry-only" in result.stdout
    assert "S5-ambiguous" in result.stdout
    assert "Research tool only" in result.stdout
    assert "Dry run only" in result.stdout


def test_demo_plan_no_dry_run() -> None:
    result = runner.invoke(app, ["demo-plan", "--no-dry-run"])
    assert result.exit_code == 0
    assert "Dry run only" not in result.stdout


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "silent-trials" in result.stdout


def test_sample_path() -> None:
    result = runner.invoke(app, ["sample-path"])
    assert result.exit_code == 0
    assert "data/sample" in result.stdout


def test_twenty_designed_samples() -> None:
    samples = load_samples()
    assert len(samples) == 20
    assert samples[0].nct_id == "NCT00000001"
    assert samples[4].sample_id == "S5-ambiguous"
    assert len(samples[4].publications) == 2


def test_match_nct_in_abstract_explains_candidates() -> None:
    result = runner.invoke(app, ["match", "--nct", "NCT00000001", "--explain"])
    assert result.exit_code == 0, result.stdout
    assert "MATCH" in result.stdout
    assert "pub-s1" in result.stdout
    assert "nct_in_text" in result.stdout
    assert "title_similarity" in result.stdout
    assert "pi_match" in result.stdout
    assert "condition_overlap" in result.stdout
    assert "date_in_window" in result.stdout
    assert "confidence=" in result.stdout


def test_match_no_nct_shows_features_individually() -> None:
    result = runner.invoke(app, ["match", "--nct", "NCT00000002", "--explain"])
    assert result.exit_code == 0, result.stdout
    assert "MATCH" in result.stdout
    assert "nct_in_text:        no" in result.stdout
    assert "title_similarity:" in result.stdout
    assert "pi_match:           yes" in result.stdout
    assert "condition_overlap:" in result.stdout
    assert "date_in_window:     yes" in result.stdout


def test_match_ambiguous_does_not_pick() -> None:
    result = runner.invoke(app, ["match", "--nct", "NCT00000005", "--explain"])
    assert result.exit_code == 0, result.stdout
    assert "AMBIGUOUS" in result.stdout
    assert "does not pick" in result.stdout
    assert "pub-s5a" in result.stdout
    assert "pub-s5b" in result.stdout
    assert "chosen:     (none" in result.stdout


def test_status_not_yet_due_prints_days() -> None:
    result = runner.invoke(app, ["status", "--nct", "NCT00000003"])
    assert result.exit_code == 0, result.stdout
    assert "NOT_YET_DUE" in result.stdout
    assert "days remaining:" in result.stdout
    assert "2027-06-06" in result.stdout


def test_status_reported_names_route() -> None:
    result = runner.invoke(app, ["status", "--nct", "NCT00000004"])
    assert result.exit_code == 0, result.stdout
    assert "REPORTED" in result.stdout
    assert "registry results module" in result.stdout
    assert "REPORTED_REGISTRY" in result.stdout


def test_match_unknown_nct_exits() -> None:
    result = runner.invoke(app, ["match", "--nct", "NCT99999999"])
    assert result.exit_code == 2


def test_demo_walkthrough() -> None:
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0, result.stdout
    assert "NCT00000001" in result.stdout
    assert "NCT00000002" in result.stdout
    assert "NCT00000005" in result.stdout
    assert "AMBIGUOUS" in result.stdout
    assert "NOT_YET_DUE" in result.stdout
    assert "REPORTED" in result.stdout


def test_report_writes_html(tmp_path: Path) -> None:
    out = tmp_path / "dashboard.html"
    result = runner.invoke(app, ["report", "--out", str(out)])
    assert result.exit_code == 0, result.stdout
    text = out.read_text(encoding="utf-8")
    assert "NCT00000001" in text
    assert "genuinely_unreported" in text or "unmatched" in text
    assert "NOT_YET_DUE" in text


def test_dashboard_html_distinguishes_buckets() -> None:
    html = render_dashboard_html()
    assert "Not a live registry" in html
    assert "NCT00000006" in html
    path = write_dashboard(Path("/tmp/silent-trials-dashboard-test.html"))
    assert path.is_file()
