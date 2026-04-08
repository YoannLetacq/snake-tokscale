"""Tests for the snake path builder (boustrophedon traversal)."""

from __future__ import annotations

import pytest

from snake_tokscale.path import build_snake_path


class TestBuildSnakePath:
    def test_length_matches_grid_size(self):
        path = build_snake_path(weeks=5, rows=7)
        assert len(path) == 5 * 7

    def test_path_stays_in_bounds(self):
        weeks, rows = 53, 7
        path = build_snake_path(weeks=weeks, rows=rows)
        for x, y in path:
            assert 0 <= x < weeks
            assert 0 <= y < rows

    def test_adjacent_steps_only(self):
        path = build_snake_path(weeks=10, rows=7)
        for prev, curr in zip(path, path[1:]):
            dx = abs(curr[0] - prev[0])
            dy = abs(curr[1] - prev[1])
            assert dx + dy == 1, f"non-adjacent step {prev} -> {curr}"

    def test_visits_every_cell_once(self):
        weeks, rows = 8, 7
        path = build_snake_path(weeks=weeks, rows=rows)
        assert len(set(path)) == weeks * rows

    def test_rejects_non_positive_dimensions(self):
        with pytest.raises(ValueError):
            build_snake_path(weeks=0, rows=7)
        with pytest.raises(ValueError):
            build_snake_path(weeks=5, rows=0)
