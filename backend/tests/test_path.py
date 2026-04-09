"""Tests for the snake path builder."""

from __future__ import annotations
import pytest
from snake_tokscale.path import build_snake_path

def _mock_cells(weeks, rows, markers=None):
    markers = markers or []
    cells = [{"level": 0} for _ in range(weeks * rows)]
    for m in markers:
        cells[m[0] * rows + m[1]]["level"] = 1
    return cells

class TestBuildSnakePath:
    def test_path_not_empty(self):
        cells = _mock_cells(5, 7, [(1, 1)])
        path, hits = build_snake_path(weeks=5, rows=7, cells=cells)
        assert len(path) > 0
        assert len(hits) == 1

    def test_path_stays_in_bounds(self):
        weeks, rows = 53, 7
        cells = _mock_cells(weeks, rows, [(10, 3)])
        path, hits = build_snake_path(weeks=weeks, rows=rows, cells=cells)
        for x, y in path:
            assert 0 <= x < weeks
            assert 0 <= y < rows

    def test_adjacent_steps_only(self):
        cells = _mock_cells(10, 7, [(5, 5)])
        path, hits = build_snake_path(weeks=10, rows=7, cells=cells)
        for i in range(len(path) - 1):
            curr, nxt = path[i], path[i + 1]
            dist = abs(curr[0] - nxt[0]) + abs(curr[1] - nxt[1])
            assert dist == 1

    def test_rejects_non_positive_dimensions(self):
        cells = _mock_cells(5, 7)
        with pytest.raises(ValueError):
            build_snake_path(weeks=0, rows=7, cells=cells)

    def test_spawn_logic_far_markers(self):
        # 20 weeks empty, then a marker
        weeks, rows = 30, 7
        cells = _mock_cells(weeks, rows, [(20, 3)])
        # first_marker_col = 20 > 17, so start_col = 20 - 13 = 7
        path, hits = build_snake_path(weeks=weeks, rows=rows, cells=cells, seed=42)
        assert path[0][0] == 7
