"""Write asciinema v2 casts from real CLI stdout. No credentials."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"


def _run(args: list[str]) -> str:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "TERM": "xterm-256color"},
    )
    return proc.stdout


def _cast(path: Path, commands: list[list[str]]) -> None:
    header = {
        "version": 2,
        "width": 140,
        "height": 48,
        "timestamp": int(time.time()),
        "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"},
    }
    events: list[list[object]] = []
    t = 0.05
    for args in commands:
        prompt = "$ " + " ".join(args) + "\r\n"
        events.append([round(t, 3), "o", prompt])
        t += 0.15
        out = _run(args)
        chunk = out.replace("\n", "\r\n")
        events.append([round(t, 3), "o", chunk])
        t += 0.40
        events.append([round(t, 3), "o", "\r\n"])
        t += 0.10
    DEMO.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(header, separators=(",", ":"))]
    lines.extend(json.dumps(ev, separators=(",", ":")) for ev in events)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {path}")


def main() -> None:
    py = [sys.executable, "-m", "silent_trials.cli"]
    # Prefer the installed console script when the venv is on PATH.
    exe = "silent-trials"
    try:
        subprocess.run([exe, "version"], cwd=ROOT, check=True, capture_output=True)
        py = [exe]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    _cast(
        DEMO / "01-matching-explained.cast",
        [
            py + ["match", "--nct", "NCT00000001", "--explain"],
            py + ["match", "--nct", "NCT00000002", "--explain"],
        ],
    )
    _cast(
        DEMO / "02-ambiguity-and-clock.cast",
        [
            py + ["match", "--nct", "NCT00000005", "--explain"],
            py + ["status", "--nct", "NCT00000003"],
            py + ["status", "--nct", "NCT00000004"],
        ],
    )
    _cast(
        DEMO / "03-evaluation.cast",
        [
            [sys.executable, "research/phase0/match_accuracy/run.py"],
            [sys.executable, "research/phase0/candidate_recall/run.py"],
            [sys.executable, "research/phase0/unmatched_split/run.py"],
        ],
    )


if __name__ == "__main__":
    main()
