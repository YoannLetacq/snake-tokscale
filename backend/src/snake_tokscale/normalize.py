"""Normalize tokscale contributions into a rectangular ``weeks × 7`` grid.

The layout mirrors the GitHub contribution heatmap: ``weeks`` columns of 7
rows (days), columns start on Sunday and end on Saturday. The grid always
contains exactly ``weeks * 7`` cells; the final column is the week containing
``end_date`` (so future days within that week are padded with zero).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TypedDict

from snake_tokscale.quantiles import compute_levels


class Cell(TypedDict):
    """A single heatmap cell."""

    date: str
    tokens: int
    level: int


DEFAULT_WEEKS = 53
DAYS_PER_WEEK = 7


def build_grid(
    contributions: list[dict],
    end_date: date,
    weeks: int = DEFAULT_WEEKS,
) -> list[Cell]:
    """Return a ``weeks * 7`` list of cells covering the window ending on ``end_date``.

    Missing days (including future days in the final week) are padded with
    zero tokens and level 0.
    """
    if not isinstance(contributions, list):
        raise TypeError("contributions must be a list of dicts")

    tokens_by_date = _extract_token_totals(contributions)
    start_date = _compute_start_sunday(end_date, weeks)

    grid_dates = [
        start_date + timedelta(days=offset)
        for offset in range(weeks * DAYS_PER_WEEK)
    ]
    window_tokens = {day.isoformat(): tokens_by_date.get(day.isoformat(), 0) for day in grid_dates}
    levels = compute_levels(window_tokens)

    return [
        Cell(date=iso, tokens=window_tokens[iso], level=levels.get(iso, 0))
        for iso in (day.isoformat() for day in grid_dates)
    ]


def _compute_start_sunday(end_date: date, weeks: int) -> date:
    """Return the Sunday that starts the ``weeks``-wide window around ``end_date``.

    The window's last column contains ``end_date``; its final cell is the
    Saturday of that week.
    """
    saturday_of_end_week = _saturday_of_week(end_date)
    total_days = weeks * DAYS_PER_WEEK
    return saturday_of_end_week - timedelta(days=total_days - 1)


def _saturday_of_week(day: date) -> date:
    """Return the Saturday that closes the Sunday→Saturday week containing ``day``."""
    # Python: Monday=0..Sunday=6; Saturday=5.
    offset_to_saturday = (5 - day.weekday()) % DAYS_PER_WEEK
    return day + timedelta(days=offset_to_saturday)


def _extract_token_totals(contributions: list[dict]) -> dict[str, int]:
    """Pull ``{date: tokens}`` out of the raw tokscale contributions list."""
    totals: dict[str, int] = {}
    for entry in contributions:
        if not isinstance(entry, dict):
            continue
        iso = entry.get("date")
        inner = entry.get("totals") or {}
        tokens = inner.get("tokens")
        if isinstance(iso, str) and isinstance(tokens, int):
            totals[iso] = tokens
    return totals
