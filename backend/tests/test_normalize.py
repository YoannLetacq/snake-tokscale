"""Tests for the normalize module (contributions → 53×7 grid)."""

from __future__ import annotations

from datetime import date

import pytest

from snake_tokscale.normalize import build_grid


def _totals_by_date(grid: list[dict]) -> dict[str, int]:
    return {cell["date"]: cell["tokens"] for cell in grid}


class TestBuildGrid:
    def test_grid_has_371_cells(self, tokscale_sample):
        grid = build_grid(tokscale_sample["contributions"], end_date=date(2026, 4, 8))
        assert len(grid) == 53 * 7

    def test_end_date_is_present(self, tokscale_sample):
        grid = build_grid(tokscale_sample["contributions"], end_date=date(2026, 4, 8))
        dates = {cell["date"] for cell in grid}
        assert "2026-04-08" in dates

    def test_last_cell_is_saturday(self, tokscale_sample):
        grid = build_grid(tokscale_sample["contributions"], end_date=date(2026, 4, 8))
        last = date.fromisoformat(grid[-1]["date"])
        # Python: Monday=0..Sunday=6, Saturday=5.
        assert last.weekday() == 5

    def test_first_cell_aligned_to_sunday(self, tokscale_sample):
        grid = build_grid(tokscale_sample["contributions"], end_date=date(2026, 4, 8))
        first_date = date.fromisoformat(grid[0]["date"])
        assert first_date.weekday() == 6  # Sunday

    def test_missing_day_is_zero(self, tokscale_sample):
        grid = build_grid(tokscale_sample["contributions"], end_date=date(2026, 4, 8))
        totals = _totals_by_date(grid)
        assert totals["2026-04-06"] == 0

    def test_known_day_tokens_populated(self, tokscale_sample):
        grid = build_grid(tokscale_sample["contributions"], end_date=date(2026, 4, 8))
        totals = _totals_by_date(grid)
        assert totals["2026-04-08"] == 2_940_221
        assert totals["2026-03-26"] == 30_642_664

    def test_every_cell_has_required_keys(self, tokscale_sample):
        grid = build_grid(tokscale_sample["contributions"], end_date=date(2026, 4, 8))
        for cell in grid:
            assert set(cell.keys()) >= {"date", "tokens", "level"}
            assert isinstance(cell["tokens"], int)
            assert 0 <= cell["level"] <= 4

    def test_rejects_non_list_contributions(self):
        with pytest.raises(TypeError):
            build_grid("nope", end_date=date(2026, 4, 8))  # type: ignore[arg-type]

    def test_empty_contributions_all_zero(self):
        grid = build_grid([], end_date=date(2026, 4, 8))
        assert len(grid) == 371
        assert all(cell["tokens"] == 0 and cell["level"] == 0 for cell in grid)
