"""Render the tokscale heatmap as a standalone SVG document.

Pure string assembly — no third-party SVG library needed. The output is
deliberately minimal so it can be embedded in a README on GitHub, whose
Markdown sanitizer strips ``<script>`` / ``<iframe>`` / event handlers but
accepts ``<svg>``, ``<rect>``, ``<g>``, and ``<animate>`` (SMIL).
"""

from __future__ import annotations
from datetime import datetime

from snake_tokscale.normalize import Cell

ROWS = 7
CELL_SIZE = 12
CELL_GAP = 2
GRID_PAD_TOP = 25
GRID_PAD_LEFT = 35
GRID_PAD_RIGHT = 10
GRID_PAD_BOTTOM = 10

# 5-level palette, tuned for dark backgrounds (tokscale purple).
LEVEL_COLORS = (
    "#161b22",  # 0 — empty
    "#3d2b5b",  # 1
    "#62448b",  # 2
    "#8959bc",  # 3
    "#b388eb",  # 4
)

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def svg_dimensions(weeks: int) -> tuple[int, int]:
    """Return the ``(width, height)`` of the SVG canvas for ``weeks`` columns."""
    width = weeks * (CELL_SIZE + CELL_GAP) - CELL_GAP + GRID_PAD_LEFT + GRID_PAD_RIGHT
    height = ROWS * (CELL_SIZE + CELL_GAP) - CELL_GAP + GRID_PAD_TOP + GRID_PAD_BOTTOM
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


def svg_header(
    weeks: int,
    cells: list[Cell] | None = None,
    background: str = "#0d1117",
) -> list[str]:
    """Return the opening ``<svg>`` / background / labels / translate ``<g>`` fragments."""
    width, height = svg_dimensions(weeks)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect class="bg" width="{width}" height="{height}" fill="{background}"/>',
        '<g class="labels" style="font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,'
        'Arial,sans-serif; font-size: 9px; fill: #8b949e;">',
    ]

    # Day labels
    parts.append(f'<text x="{GRID_PAD_LEFT - 25}" y="{GRID_PAD_TOP + cell_y(1) + 9}">Mon</text>')
    parts.append(f'<text x="{GRID_PAD_LEFT - 25}" y="{GRID_PAD_TOP + cell_y(3) + 9}">Wed</text>')
    parts.append(f'<text x="{GRID_PAD_LEFT - 25}" y="{GRID_PAD_TOP + cell_y(5) + 9}">Fri</text>')

    # Month labels
    if cells:
        last_month = -1
        for col in range(weeks):
            cell = cells[col * ROWS]
            if cell.get("date"):
                try:
                    dt = datetime.fromisoformat(cell["date"])
                    month = dt.month - 1
                    if month != last_month:
                        x = GRID_PAD_LEFT + cell_x(col)
                        y = GRID_PAD_TOP - 8
                        parts.append(f'<text x="{x}" y="{y}">{MONTHS[month]}</text>')
                        last_month = month
                except ValueError:
                    pass

    parts.append("</g>")
    parts.append(f'<g class="cells" transform="translate({GRID_PAD_LEFT},{GRID_PAD_TOP})">')
    return parts


def cell_x(col: int) -> int:
    return col * (CELL_SIZE + CELL_GAP)


def cell_y(row: int) -> int:
    return row * (CELL_SIZE + CELL_GAP)


def render_grid_svg(cells: list[Cell], weeks: int) -> str:
    """Return a self-contained SVG string with one ``<rect>`` per cell."""
    expected = weeks * ROWS
    if len(cells) != expected:
        raise ValueError(f"expected {expected} cells for {weeks} weeks, got {len(cells)}")

    parts = svg_header(weeks, cells=cells)

    for _col, _row, x, y, level, _cell in iter_cell_positions(cells):
        color = LEVEL_COLORS[level]
        parts.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" ry="2" fill="{color}"/>'
        )

    parts.append("</g></svg>")
    return "".join(parts)
