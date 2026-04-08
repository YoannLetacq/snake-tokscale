"""Tests for the animated snake SVG renderer."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from snake_tokscale.animate import render_animated_snake
from snake_tokscale.normalize import Cell

SVG_NS = "{http://www.w3.org/2000/svg}"


def _cells(n: int) -> list[Cell]:
    return [
        Cell(date=f"2026-01-{(i % 28) + 1:02d}", tokens=i * 100, level=(i % 5))
        for i in range(n)
    ]


class TestRenderAnimatedSnake:
    def test_output_is_valid_svg(self):
        svg = render_animated_snake(_cells(21), weeks=3, snake_length=4, duration_s=10.0)
        root = ET.fromstring(svg)
        assert root.tag == f"{SVG_NS}svg"

    def test_contains_animate_elements(self):
        svg = render_animated_snake(_cells(21), weeks=3, snake_length=4, duration_s=10.0)
        root = ET.fromstring(svg)
        animates = root.findall(f".//{SVG_NS}animate")
        # At least one <animate> per snake segment (x + y) + cell fades.
        assert len(animates) >= 4 * 2

    def test_contains_snake_segments(self):
        svg = render_animated_snake(_cells(21), weeks=3, snake_length=4, duration_s=10.0)
        root = ET.fromstring(svg)
        snake_rects = [
            rect
            for rect in root.findall(f".//{SVG_NS}rect")
            if rect.attrib.get("class") == "snake-segment"
        ]
        assert len(snake_rects) == 4

    def test_rejects_invalid_snake_length(self):
        import pytest

        with pytest.raises(ValueError):
            render_animated_snake(_cells(21), weeks=3, snake_length=0, duration_s=10.0)
