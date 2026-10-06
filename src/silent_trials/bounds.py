"""Wilson score interval for a binomial proportion.

Used so an unmatched-split fraction is never shown as a point estimate
without bounds. This is a statistical interval on the committed
adjudication set, not a sampling interval over live ClinicalTrials.gov.
"""

from __future__ import annotations

import math


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Return (low, high) Wilson score bounds. Empty n yields (0, 1)."""

    if n <= 0:
        return (0.0, 1.0)
    p = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return (max(0.0, center - margin), min(1.0, center + margin))
