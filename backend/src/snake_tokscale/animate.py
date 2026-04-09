"""Render an animated snake SVG that traverses the tokscale heatmap.

The output uses SMIL ``<animate>`` tags — the only animation primitive allowed
by GitHub's Markdown sanitizer. The snake follows a randomized greedy path
towards contribution markers.
"""

from __future__ import annotations
import time

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

    # Use current time as seed for randomization on each run
    seed = int(time.time())
    path = build_snake_path(weeks=weeks, rows=ROWS, cells=cells, seed=seed)
    
    # Adjust duration based on path length if needed, or keep fixed
    # One step every ~0.15s looks reasonable
    actual_duration = len(path) * 0.15

    parts = svg_header(weeks, cells=cells, background=BACKGROUND_COLOR)
    parts.extend(_render_cells(cells, path, actual_duration))
    parts.extend(_render_snake(path, snake_length, actual_duration))
    parts.append("</g></svg>")
    return "".join(parts)


def _render_cells(
    cells: list[Cell],
    path: list[tuple[int, int]],
    duration_s: float,
) -> list[str]:
    """Emit ``<rect>`` elements for every heatmap cell with fade-out animations."""
    steps = len(path)
    # Only fade out the FIRST time the snake reaches a cell
    path_index = {}
    for i, coord in enumerate(path):
        if coord not in path_index:
            path_index[coord] = i
            
    pieces: list[str] = []

    for col, row, x, y, level, _cell in iter_cell_positions(cells):
        base_color = LEVEL_COLORS[level]
        rect = (
            f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" ry="2" fill="{base_color}">'
        )
        if level > 0 and (col, row) in path_index:
            rect += _fade_animation(path_index[(col, row)], steps, base_color, duration_s)
        rect += "</rect>"
        pieces.append(rect)

    return pieces


def _fade_animation(step: int, steps: int, base_color: str, duration_s: float) -> str:
    """Return a ``<animate>`` fragment that fades a cell to the empty palette."""
    when = min(max(step / max(steps - 1, 1), 0.0001), 0.9999)
    # Transition duration: ~2 steps
    step_pct = 1.0 / steps
    end_pct = min(when + step_pct * 2, 1.0)
    
    return (
        f'<animate attributeName="fill" '
        f'dur="{duration_s}s" repeatCount="indefinite" '
        f'calcMode="linear" fill="freeze" '
        f'keyTimes="0;{when:.4f};{end_pct:.4f};1" '
        f'values="{base_color};{base_color};{LEVEL_COLORS[0]};{LEVEL_COLORS[0]}"/>'
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
        # Segment ``seg`` lags behind the head by ``seg`` positions. 
        # We wrap around for the animation loop.
        shifted_x = []
        shifted_y = []
        for i in range(steps):
            idx = (i - seg) % steps
            shifted_x.append(x_values[idx])
            shifted_y.append(y_values[idx])
            
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
