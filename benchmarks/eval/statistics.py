"""Small dependency-free statistics used by future HelixAgent evaluations."""

from __future__ import annotations

import math
from statistics import fmean, stdev
from typing import Sequence


def mean_and_sample_std(values: Sequence[float]) -> tuple[float, float]:
    """Return arithmetic mean and Bessel-corrected sample standard deviation."""
    if len(values) < 2:
        raise ValueError("at least two observations are required")
    return fmean(values), stdev(values)


def wilson_interval(successes: int, trials: int, z_score: float = 1.959963984540054) -> tuple[float, float]:
    """Return a two-sided Wilson interval for a binomial proportion."""
    if trials <= 0:
        raise ValueError("trials must be positive")
    if not 0 <= successes <= trials:
        raise ValueError("successes must be within [0, trials]")
    if z_score <= 0:
        raise ValueError("z_score must be positive")

    proportion = successes / trials
    z_squared = z_score * z_score
    denominator = 1 + z_squared / trials
    center = (proportion + z_squared / (2 * trials)) / denominator
    margin = z_score * math.sqrt(
        proportion * (1 - proportion) / trials + z_squared / (4 * trials * trials)
    ) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)
