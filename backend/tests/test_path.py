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
    def test_path_covers_all_cells(self):
        weeks, rows = 5, 7
        cells = _mock_cells(weeks, rows, [(1, 1)])
        path, _ = build_snake_path(weeks=weeks, rows=rows, cells=cells)
        assert len(path) == weeks * rows
        assert len(set(path)) == weeks * rows

    def test_hits_identified_correctly(self):
        weeks, rows = 2, 7
        markers = {(0, 0), (1, 6)}
        cells = _mock_cells(weeks, rows, list(markers))
        path, hits = build_snake_path(weeks=weeks, rows=rows, cells=cells, seed=42)
        # Hits must line up with the actual marker positions along the path,
        # regardless of which random trajectory the DFS produced.
        expected = sorted(i for i, coord in enumerate(path) if coord in markers)
        assert sorted(hits) == expected
        assert len(hits) == 2

    def test_path_stays_in_bounds(self):
        weeks, rows = 53, 7
        cells = _mock_cells(weeks, rows, [(10, 3)])
        path, _ = build_snake_path(weeks=weeks, rows=rows, cells=cells)
        for x, y in path:
            assert 0 <= x < weeks
            assert 0 <= y < rows

    def test_adjacent_steps_only(self):
        cells = _mock_cells(10, 7, [(5, 5)])
        path, _ = build_snake_path(weeks=10, rows=7, cells=cells)
        for i in range(len(path) - 1):
            curr, nxt = path[i], path[i + 1]
            dist = abs(curr[0] - nxt[0]) + abs(curr[1] - nxt[1])
            assert dist == 1

    def test_rejects_non_positive_dimensions(self):
        cells = _mock_cells(5, 7)
        with pytest.raises(ValueError):
            build_snake_path(weeks=0, rows=7, cells=cells)
