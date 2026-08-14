"""Hand-verifiable tests for benchmark aggregation statistics."""

from math import isclose

import pytest

from benchmarks.eval.statistics import mean_and_sample_std, wilson_interval


def test_mean_and_sample_std_for_three_consecutive_values() -> None:
    mean, sample_std = mean_and_sample_std([1.0, 2.0, 3.0])

    assert mean == 2.0
    assert sample_std == 1.0


def test_wilson_interval_for_half_successes_has_known_bounds() -> None:
    lower, upper = wilson_interval(5, 10)

    assert isclose(lower, 0.236593, rel_tol=0, abs_tol=1e-6)
    assert isclose(upper, 0.763407, rel_tol=0, abs_tol=1e-6)


@pytest.mark.parametrize(
    ("successes", "trials"),
    [(-1, 2), (3, 2), (0, 0)],
)
def test_wilson_interval_rejects_invalid_counts(successes: int, trials: int) -> None:
    with pytest.raises(ValueError):
        wilson_interval(successes, trials)
