"""Render the tokscale heatmap as a standalone SVG document.

Pure string assembly — no third-party SVG library needed.
"""

from __future__ import annotations
import random
from datetime import datetime
from dataclasses import dataclass

from snake_tokscale.normalize import Cell

ROWS = 7
CELL_SIZE = 12
CELL_GAP = 2
GRID_PAD_TOP = 25
GRID_PAD_LEFT = 35
GRID_PAD_RIGHT = 10
GRID_PAD_BOTTOM = 10


@dataclass(frozen=True)
class Palette:
    """A color scheme for the heatmap and snake."""

    name: str
    levels: tuple[str, str, str, str, str]
    snake: str
    head: str


PALETTES = (
    Palette(
        name="purple",
        levels=("#161b22", "#3d2b5b", "#62448b", "#8959bc", "#b388eb"),
        snake="#e84749",
        head="#ff7b72",
    ),
    Palette(
        name="green",
        levels=("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"),
        snake="#f1e05a",
        head="#fff275",
    ),
    Palette(
        name="blue",
        levels=("#161b22", "#073069", "#0969da", "#54aeff", "#b1bac4"),
        snake="#ff7b72",
        head="#ffa198",
    ),
    Palette(
        name="orange",
        levels=("#161b22", "#5c2b00", "#953800", "#cb4b16", "#fb8f44"),
        snake="#79c0ff",
        head="#a5d6ff",
    ),
)

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def get_random_palette() -> Palette:
    """Return a random color scheme."""
    return random.choice(PALETTES)


def svg_dimensions(weeks: int) -> tuple[int, int]:
    """Return the ``(width, height)`` of the SVG canvas for ``weeks`` columns."""
    width = weeks * (CELL_SIZE + CELL_GAP) - CELL_GAP + GRID_PAD_LEFT + GRID_PAD_RIGHT
    height = ROWS * (CELL_SIZE + CELL_GAP) - CELL_GAP + GRID_PAD_TOP + GRID_PAD_BOTTOM
    return width, height


def iter_cell_positions(cells: list[Cell], palette: Palette):
    """Yield ``(col, row, x, y, level, color)`` tuples for each cell."""
    for idx, cell in enumerate(cells):
        col = idx // ROWS
        row = idx % ROWS
        x = col * (CELL_SIZE + CELL_GAP)
        y = row * (CELL_SIZE + CELL_GAP)
        level = max(0, min(4, cell["level"]))
        color = palette.levels[level]
        yield col, row, x, y, level, color


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

    parts.append(f'<text x="{GRID_PAD_LEFT - 25}" y="{GRID_PAD_TOP + cell_y(1) + 9}">Mon</text>')
    parts.append(f'<text x="{GRID_PAD_LEFT - 25}" y="{GRID_PAD_TOP + cell_y(3) + 9}">Wed</text>')
    parts.append(f'<text x="{GRID_PAD_LEFT - 25}" y="{GRID_PAD_TOP + cell_y(5) + 9}">Fri</text>')

    if cells:
        last_month = -1
        for col in range(weeks):
            cell = cells[col * ROWS]
            if cell.get("date"):
                try:
                    dt = datetime.fromisoformat(cell["date"])
                    month = dt.month - 1
                    if month != last_month:
                        parts.append(
                            f'<text x="{GRID_PAD_LEFT + cell_x(col)}" '
                            f'y="{GRID_PAD_TOP - 8}">{MONTHS[month]}</text>'
                        )
                        last_month = month
                except ValueError:
                    pass

    parts.append("</g>")
    parts.append(f'<g class="cells" transform="translate({GRID_PAD_LEFT},{GRID_PAD_TOP})">')
    return parts


def cell_x(col: int) -> int:
    """Horizontal offset for a column."""
    return col * (CELL_SIZE + CELL_GAP)


def cell_y(row: int) -> int:
    """Vertical offset for a row."""
    return row * (CELL_SIZE + CELL_GAP)


def render_grid_svg(cells: list[Cell], weeks: int) -> str:
    """Return a self-contained SVG string with one ``<rect>`` per cell."""
    expected = weeks * ROWS
    if len(cells) != expected:
        raise ValueError(f"expected {expected} cells for {weeks} weeks, got {len(cells)}")

    palette = get_random_palette()
    parts = svg_header(weeks, cells=cells)

    for _col, _row, x, y, _level, color in iter_cell_positions(cells, palette):
        parts.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" ry="2" fill="{color}"/>'
        )

    parts.append("</g></svg>")
    return "".join(parts)
