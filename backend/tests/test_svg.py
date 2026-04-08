"""Tests for the static SVG heatmap renderer."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from snake_tokscale.normalize import Cell
from snake_tokscale.svg import render_grid_svg

SVG_NS = "{http://www.w3.org/2000/svg}"


def _make_cells(n: int) -> list[Cell]:
    return [
        Cell(date=f"2026-01-{(i % 28) + 1:02d}", tokens=i * 100, level=i % 5)
        for i in range(n)
    ]


class TestRenderGridSvg:
    def test_contains_one_rect_per_cell(self):
        cells = _make_cells(21)  # 3 weeks × 7
        svg = render_grid_svg(cells, weeks=3)
        root = ET.fromstring(svg)
        cell_rects = [
            r for r in root.findall(f".//{SVG_NS}rect") if r.attrib.get("class") == "cell"
        ]
        assert len(cell_rects) == 21

    def test_root_has_declared_dimensions(self):
        svg = render_grid_svg(_make_cells(371), weeks=53)
        root = ET.fromstring(svg)
        assert root.attrib["width"]
        assert root.attrib["height"]
        assert root.attrib["viewBox"]

    def test_rects_use_palette_for_levels(self):
        cells = _make_cells(7)  # 1 week × 7 rows
        svg = render_grid_svg(cells, weeks=1)
        root = ET.fromstring(svg)
        cell_rects = [
            r for r in root.findall(f".//{SVG_NS}rect") if r.attrib.get("class") == "cell"
        ]
        assert cell_rects
        for rect in cell_rects:
            assert rect.attrib["fill"].startswith("#")

    def test_mismatched_cell_count_raises(self):
        with pytest.raises(ValueError):
            render_grid_svg(_make_cells(10), weeks=3)
