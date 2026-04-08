"""Render the tokscale heatmap as a standalone SVG document.

Pure string assembly — no third-party SVG library needed. The output is
deliberately minimal so it can be embedded in a README on GitHub, whose
Markdown sanitizer strips ``<script>`` / ``<iframe>`` / event handlers but
accepts ``<svg>``, ``<rect>``, ``<g>``, and ``<animate>`` (SMIL).
"""

from __future__ import annotations

from snake_tokscale.normalize import Cell

ROWS = 7
CELL_SIZE = 12
CELL_GAP = 2
GRID_PAD = 10

# 5-level palette, tuned for dark backgrounds.
LEVEL_COLORS = (
    "#161b22",  # 0 — empty
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4
)


def svg_dimensions(weeks: int) -> tuple[int, int]:
    """Return the ``(width, height)`` of the SVG canvas for ``weeks`` columns."""
    width = weeks * (CELL_SIZE + CELL_GAP) - CELL_GAP + 2 * GRID_PAD
    height = ROWS * (CELL_SIZE + CELL_GAP) - CELL_GAP + 2 * GRID_PAD
    return width, height


def iter_cell_positions(cells: list[Cell]):
    """Yield ``(col, row, x, y, level, cell)`` tuples for each heatmap cell."""
    for idx, cell in enumerate(cells):
        col = idx // ROWS
        row = idx % ROWS
        x = col * (CELL_SIZE + CELL_GAP)
        y = row * (CELL_SIZE + CELL_GAP)
        level = max(0, min(4, cell["level"]))
        yield col, row, x, y, level, cell


def svg_header(weeks: int, background: str = "#0d1117") -> list[str]:
    """Return the opening ``<svg>`` / background / translate ``<g>`` fragments."""
    width, height = svg_dimensions(weeks)
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect class="bg" width="{width}" height="{height}" fill="{background}"/>',
        f'<g class="cells" transform="translate({GRID_PAD},{GRID_PAD})">',
    ]


def render_grid_svg(cells: list[Cell], weeks: int) -> str:
    """Return a self-contained SVG string with one ``<rect>`` per cell."""
    expected = weeks * ROWS
    if len(cells) != expected:
        raise ValueError(f"expected {expected} cells for {weeks} weeks, got {len(cells)}")

    parts = svg_header(weeks)

    for _col, _row, x, y, level, _cell in iter_cell_positions(cells):
        color = LEVEL_COLORS[level]
        parts.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" ry="2" fill="{color}"/>'
        )

    parts.append("</g></svg>")
    return "".join(parts)
