"""Static HTML dashboard from the committed sample catalog.

This is not a live ClinicalTrials.gov site. It exists so a reviewer can
see match decisions, the FDAAA clock, and the unmatched split without
credentials or a network.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from silent_trials import REFERENCE_DATE_ISO, SAFETY_DISCLAIMER
from silent_trials.catalog import load_samples
from silent_trials.fdaaa import REFERENCE_DATE, evaluate_clock
from silent_trials.matcher import match_trial
from silent_trials.reporting import combine_outcome, sponsor_counts

ROUTE_LABEL = {
    "REPORTED_REGISTRY": "registry results module",
    "REPORTED_PUBLICATION": "matched journal publication",
    "REPORTED_BOTH": "registry results and matched publication",
}


def _bucket(outcome: str, decision: str) -> str:
    if outcome in {"REPORTED_REGISTRY", "REPORTED_PUBLICATION", "REPORTED_BOTH"}:
        return "reported"
    if outcome == "NOT_YET_DUE":
        return "not_yet_due"
    if outcome == "NOT_APPLICABLE":
        return "not_applicable"
    if decision == "AMBIGUOUS":
        return "ambiguous_unmatched"
    if decision == "NO_MATCH" and outcome == "SILENT":
        return "genuinely_unreported_on_this_catalog"
    return "unmatched"


def render_dashboard_html() -> str:
    samples = load_samples()
    rows: list[str] = []
    outcomes = []
    for sample in samples:
        match = match_trial(sample.trial, sample.publications)
        clock = evaluate_clock(sample.trial, reference=REFERENCE_DATE)
        combined = combine_outcome(sample.trial, match)
        outcomes.append(combined)
        route = ROUTE_LABEL.get(clock.status, "none")
        bucket = _bucket(combined.outcome, match.decision)
        chosen = match.chosen_pub_id or "—"
        remaining = str(clock.days_remaining) if clock.days_remaining is not None else "—"
        rows.append(
            "<tr>"
            f"<td>{escape(sample.nct_id)}</td>"
            f"<td>{escape(sample.sample_id)}</td>"
            f"<td>{escape(match.decision)}</td>"
            f"<td>{escape(chosen)}</td>"
            f"<td>{escape(clock.status)}</td>"
            f"<td>{escape(route)}</td>"
            f"<td>{escape(remaining)}</td>"
            f"<td>{escape(combined.outcome)}</td>"
            f"<td>{escape(bucket)}</td>"
            "</tr>"
        )
    counts = sponsor_counts(outcomes)
    sponsor_rows = []
    for sponsor, tally in sorted(counts.items()):
        sponsor_rows.append(
            "<tr>"
            f"<td>{escape(sponsor)}</td>"
            f"<td>{tally['n']}</td>"
            f"<td>{tally['silent']}</td>"
            f"<td>{tally['reported']}</td>"
            f"<td>{tally['not_yet_due']}</td>"
            f"<td>{tally['not_applicable']}</td>"
            "</tr>"
        )
    table = "\n".join(rows)
    sponsors = "\n".join(sponsor_rows)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>silent-trials sample dashboard</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 2rem; max-width: 1100px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 0.92rem; }}
    th, td {{
      border: 1px solid #ccc; padding: 0.4rem 0.5rem;
      text-align: left; vertical-align: top;
    }}
    th {{ background: #f4f4f4; }}
    .note {{ background: #fff8e1; border: 1px solid #e0c36c; padding: 0.8rem 1rem; }}
    code {{ font-size: 0.9em; }}
  </style>
</head>
<body>
  <h1>silent-trials sample dashboard</h1>
  <p class="note"><strong>Not a live registry.</strong> {escape(SAFETY_DISCLAIMER)}
  Reference date {escape(REFERENCE_DATE_ISO)}. This page is generated from
  <code>data/sample/samples.json</code>. Unmatched is not the same as unreported:
  the matcher can miss a paper, two papers can tie (AMBIGUOUS), and a trial
  inside the 12-month window is NOT_YET_DUE. Treating every unmatched NCT as
  silent overstates non-reporting. See <code>docs/METHODOLOGY.md</code>.</p>
  <h2>Designed catalog (n=20)</h2>
  <table>
    <thead>
      <tr>
        <th>NCT</th><th>sample</th><th>match</th><th>chosen</th>
        <th>clock</th><th>posting route</th><th>days remaining</th>
        <th>outcome</th><th>bucket</th>
      </tr>
    </thead>
    <tbody>
      {table}
    </tbody>
  </table>
  <h2>Sponsor tallies on this catalog only</h2>
  <p>Designed-probe counts. Not a ranking. Not an FDAAA enforcement list.</p>
  <table>
    <thead>
      <tr><th>sponsor</th><th>n</th><th>silent</th><th>reported</th>
      <th>not_yet_due</th><th>not_applicable</th></tr>
    </thead>
    <tbody>
      {sponsors}
    </tbody>
  </table>
</body>
</html>
"""


def write_dashboard(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_dashboard_html(), encoding="utf-8")
    return path
