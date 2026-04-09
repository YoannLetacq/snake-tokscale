"""Render an animated snake SVG that traverses the tokscale heatmap.

The output uses SMIL ``<animate>`` tags — the only animation primitive allowed
by GitHub's Markdown sanitizer. The snake follows a boustrophedon path over
every cell; each body segment replays the head's trajectory one step behind.
Cells with ``level > 0`` fade to the empty palette colour when the head
reaches them, giving a "snake eats the grid" impression.
"""

from __future__ import annotations

from snake_tokscale.normalize import Cell
from snake_tokscale.path import build_snake_path
from snake_tokscale.svg import (
    CELL_GAP,
    CELL_SIZE,
    LEVEL_COLORS,
    ROWS,
    iter_cell_positions,
    svg_header,
)

SNAKE_COLOR = "#e84749"
SNAKE_HEAD_COLOR = "#ff7b72"
BACKGROUND_COLOR = "#0d1117"


def render_animated_snake(
    cells: list[Cell],
    weeks: int,
    snake_length: int = 4,
    duration_s: float = 30.0,
) -> str:
    """Return an animated SVG snake traversing the heatmap defined by ``cells``."""
    if snake_length <= 0:
        raise ValueError("snake_length must be positive")
    expected = weeks * ROWS
    if len(cells) != expected:
        raise ValueError(f"expected {expected} cells for {weeks} weeks, got {len(cells)}")

    path = build_snake_path(weeks=weeks, rows=ROWS)
    parts = svg_header(weeks, cells=cells, background=BACKGROUND_COLOR)
    parts.extend(_render_cells(cells, path, duration_s))
    parts.extend(_render_snake(path, snake_length, duration_s))
    parts.append("</g></svg>")
    return "".join(parts)


def _render_cells(
    cells: list[Cell],
    path: list[tuple[int, int]],
    duration_s: float,
) -> list[str]:
    """Emit ``<rect>`` elements for every heatmap cell with fade-out animations."""
    steps = len(path)
    path_index = {coord: i for i, coord in enumerate(path)}
    pieces: list[str] = []

    for col, row, x, y, level, _cell in iter_cell_positions(cells):
        base_color = LEVEL_COLORS[level]
        rect = (
            f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" ry="2" fill="{base_color}">'
        )
        if level > 0:
            rect += _fade_animation(path_index.get((col, row)), steps, base_color, duration_s)
        rect += "</rect>"
        pieces.append(rect)

    return pieces


def _fade_animation(step: int | None, steps: int, base_color: str, duration_s: float) -> str:
    """Return a ``<animate>`` fragment that fades a cell to the empty palette."""
    if step is None:
        return ""
    when = min(max(step / max(steps - 1, 1), 0.0001), 0.9999)
    return (
        f'<animate attributeName="fill" '
        f'values="{base_color};{LEVEL_COLORS[0]}" '
        f'keyTimes="{when:.4f};{min(when + 0.02, 1.0):.4f}" '
        f'dur="{duration_s}s" repeatCount="indefinite" '
        f'calcMode="linear" fill="freeze"/>'
    )


def _render_snake(
    path: list[tuple[int, int]],
    snake_length: int,
    duration_s: float,
) -> list[str]:
    """Emit ``<rect>`` elements with ``<animate>`` for each snake segment."""
    pieces: list[str] = []
    x_values = [str(col * (CELL_SIZE + CELL_GAP) + 1) for col, _ in path]
    y_values = [str(row * (CELL_SIZE + CELL_GAP) + 1) for _, row in path]

    steps = len(path)
    for seg in range(snake_length):
        # Segment ``seg`` lags behind the head by ``seg`` positions. We shift
        # the value lists so all segments share the same keyTimes.
        shift = seg
        shifted_x = (x_values[-shift:] if shift else []) + x_values[: steps - shift]
        shifted_y = (y_values[-shift:] if shift else []) + y_values[: steps - shift]
        color = SNAKE_HEAD_COLOR if seg == 0 else SNAKE_COLOR
        size = CELL_SIZE - 2
        pieces.append(
            f'<rect class="snake-segment" width="{size}" height="{size}" rx="3" ry="3" '
            f'fill="{color}" x="{shifted_x[0]}" y="{shifted_y[0]}">'
            f'<animate attributeName="x" values="{";".join(shifted_x)}" '
            f'dur="{duration_s}s" repeatCount="indefinite" calcMode="discrete"/>'
            f'<animate attributeName="y" values="{";".join(shifted_y)}" '
            f'dur="{duration_s}s" repeatCount="indefinite" calcMode="discrete"/>'
            f'</rect>'
        )
    return pieces
