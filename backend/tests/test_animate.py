"""Tests for the animated snake SVG renderer."""

from __future__ import annotations
import xml.etree.ElementTree as ET
from snake_tokscale.animate import render_animated_snake

SVG_NS = "{http://www.w3.org/2000/svg}"

def _cells(n: int):
    return [{"date": "2026-01-01", "tokens": 100, "level": 1} for _ in range(n)]

class TestRenderAnimatedSnake:
    def test_output_is_valid_svg(self):
        svg, _pal = render_animated_snake(_cells(21), weeks=3, snake_length=4)
        root = ET.fromstring(svg)
        assert root.tag == f"{SVG_NS}svg"

    def test_contains_animate_elements(self):
        svg, _pal = render_animated_snake(_cells(21), weeks=3, snake_length=4)
        root = ET.fromstring(svg)
        animates = root.findall(f".//{SVG_NS}animate")
        assert len(animates) > 0

    def test_rejects_invalid_snake_length(self):
        import pytest
        with pytest.raises(ValueError):
            render_animated_snake(_cells(21), weeks=3, snake_length=0)

    def test_returns_palette(self):
        _svg, pal = render_animated_snake(_cells(21), weeks=3, snake_length=4)
        assert pal.name
        assert len(pal.levels) == 5
