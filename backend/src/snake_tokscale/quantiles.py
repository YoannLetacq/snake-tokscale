"""Quantile bucketing for tokscale daily totals.

Maps raw token counts to discrete levels (0-4) used by the heatmap palette:

- level 0: day with zero tokens
- level 1..4: quartile buckets (p25, p50, p75) over the non-zero days
"""

from __future__ import annotations

from statistics import quantiles as _stats_quantiles


def compute_levels(tokens_by_date: dict[str, int]) -> dict[str, int]:
    """Return a ``{date: level}`` mapping computed from raw token totals.

    Days with ``tokens == 0`` always map to level 0. Non-zero days are bucketed
    into four quartiles. If every non-zero day shares the same value, they all
    collapse to level 1 (avoiding division-by-zero noise).
    """
    if not tokens_by_date:
        return {}

    non_zero = [value for value in tokens_by_date.values() if value > 0]
    if not non_zero:
        return {key: 0 for key in tokens_by_date}

    thresholds = _compute_thresholds(non_zero)
    return {
        key: 0 if value == 0 else _bucket(value, thresholds)
        for key, value in tokens_by_date.items()
    }


def _compute_thresholds(values: list[int]) -> tuple[float, float, float] | None:
    """Return (p25, p50, p75) thresholds, or ``None`` if not computable."""
    unique = set(values)
    if len(unique) < 2 or len(values) < 4:
        return None
    q1, q2, q3 = _stats_quantiles(values, n=4)
    return q1, q2, q3


def _bucket(value: int, thresholds: tuple[float, float, float] | None) -> int:
    """Assign a 1-4 level given the quartile thresholds (or 1 if uniform)."""
    if thresholds is None:
        return 1
    q1, q2, q3 = thresholds
    if value <= q1:
        return 1
    if value <= q2:
        return 2
    if value <= q3:
        return 3
    return 4
