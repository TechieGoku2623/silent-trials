from __future__ import annotations

from typer.testing import CliRunner

from silent_trials.cli import app, load_samples

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
