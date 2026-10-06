from __future__ import annotations

from silent_trials.bounds import wilson_interval


def test_wilson_empty() -> None:
    low, high = wilson_interval(0, 0)
    assert low == 0.0
    assert high == 1.0


def test_wilson_known_range() -> None:
    low, high = wilson_interval(42, 100)
    assert 0.32 < low < 0.36
    assert 0.51 < high < 0.52
    assert low < 0.42 < high


def test_wilson_all_success() -> None:
    low, high = wilson_interval(100, 100)
    assert low > 0.95
    assert high == 1.0
    zero_low, zero_high = wilson_interval(0, 100)
    assert zero_low == 0.0
    assert zero_high < 0.05
