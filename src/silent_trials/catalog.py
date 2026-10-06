"""Load the committed sample catalog. No network."""

from __future__ import annotations

import json

from silent_trials.config import get_settings
from silent_trials.schemas import SampleCase


def load_samples() -> list[SampleCase]:
    path = get_settings().sample_dir / "samples.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [SampleCase.model_validate(item) for item in raw["samples"]]


def sample_by_nct(nct_id: str) -> SampleCase:
    wanted = nct_id.strip().upper()
    for sample in load_samples():
        if sample.nct_id.upper() == wanted:
            return sample
    known = ", ".join(s.nct_id for s in load_samples())
    raise KeyError(f"NCT {nct_id} is not in the committed sample catalog. Known: {known}")
