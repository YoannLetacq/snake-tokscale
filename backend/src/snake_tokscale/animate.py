"""Render an animated snake SVG that traverses the tokscale heatmap.

The output uses SMIL ``<animate>`` tags — the only animation primitive allowed
by GitHub's Markdown sanitizer. The snake follows a randomized greedy path
towards contribution markers and grows as it eats them.
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
    _duration_s: float = 30.0,
) -> str:
    """Return an animated SVG snake traversing the heatmap defined by ``cells``."""
    if snake_length <= 0:
        raise ValueError("snake_length must be positive")
    expected = weeks * ROWS
    if len(cells) != expected:
        raise ValueError(f"expected {expected} cells for {weeks} weeks, got {len(cells)}")

    seed = int(time.time())
    path, hits = build_snake_path(weeks=weeks, rows=ROWS, cells=cells, seed=seed)

    # One step every ~0.15s
    actual_duration = len(path) * 0.15

    parts = svg_header(weeks, cells=cells, background=BACKGROUND_COLOR)
    parts.extend(_render_cells(cells, path, actual_duration))
    parts.extend(_render_snake(path, hits, actual_duration))
    parts.append("</g></svg>")
    return "".join(parts)


def _render_cells(
    cells: list[Cell],
    path: list[tuple[int, int]],
    duration_s: float,
) -> list[str]:
    """Emit ``<rect> deserted by head with fade-out animations."""
    path_index = _build_path_index(path)
    pieces: list[str] = []

    for col, row, x, y, level, _cell in iter_cell_positions(cells):
        base_color = LEVEL_COLORS[level]
        rect = (
            f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" ry="2" fill="{base_color}">'
        )
        if level > 0 and (col, row) in path_index:
            rect += _fade_animation(path_index[(col, row)], len(path), base_color, duration_s)
        rect += "</rect>"
        pieces.append(rect)

    return pieces


def _build_path_index(path: list[tuple[int, int]]) -> dict[tuple[int, int], int]:
    index = {}
    for i, coord in enumerate(path):
        if coord not in index:
            index[coord] = i
    return index


def _fade_animation(step: int, steps: int, base_color: str, duration_s: float) -> str:
    """Return a ``<animate>`` fragment that fades a cell to the empty palette."""
    when = min(max(step / max(steps - 1, 1), 0.0001), 0.9999)
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
    hits: list[int],
    duration_s: float,
) -> list[str]:
    """Emit snake segments that grow as markers are hit."""
    pieces: list[str] = []
    x_values = [str(col * (CELL_SIZE + CELL_GAP) + 1) for col, _ in path]
    y_values = [str(row * (CELL_SIZE + CELL_GAP) + 1) for _, row in path]
    steps = len(path)

    # Map for helper to avoid too many arguments
    path_data = {
        "x": x_values,
        "y": y_values,
        "steps": steps,
        "duration": duration_s
    }

    # Starts with head (seg 0), grows for each hit (seg 1..len(hits)).
    # Cap at 50 to avoid massive SVGs.
    max_segments = min(len(hits) + 1, 50)
    appearance_steps = [0] + hits

    for seg_idx in range(max_segments):
        start_step = appearance_steps[seg_idx]
        pieces.append(_render_segment(seg_idx, start_step, path_data))

    return pieces


def _render_segment(
    seg_idx: int,
    start_step: int,
    data: dict,
) -> str:
    steps = data["steps"]
    duration_s = data["duration"]
    shifted_x = []
    shifted_y = []
    for i in range(steps):
        idx = (i - seg_idx) % steps
        shifted_x.append(data["x"][idx])
        shifted_y.append(data["y"][idx])

    color = SNAKE_HEAD_COLOR if seg_idx == 0 else SNAKE_COLOR
    size = CELL_SIZE - 2
    start_pct = start_step / max(steps - 1, 1)
    visibility = "visible" if seg_idx == 0 else "hidden"

    rect = (
        f'<rect class="snake-segment" width="{size}" height="{size}" rx="3" ry="3" '
        f'fill="{color}" x="{shifted_x[0]}" y="{shifted_y[0]}" visibility="{visibility}">'
    )
    if seg_idx > 0:
        rect += (
            f'<animate attributeName="visibility" from="hidden" to="visible" '
            f'begin="{start_pct * duration_s:.4f}s" dur="{duration_s:.4f}s" '
            f'repeatCount="indefinite" fill="freeze"/>'
        )
    rect += (
        f'<animate attributeName="x" values="{";".join(shifted_x)}" '
        f'dur="{duration_s}s" repeatCount="indefinite" calcMode="discrete"/>'
        f'<animate attributeName="y" values="{";".join(shifted_y)}" '
        f'dur="{duration_s}s" repeatCount="indefinite" calcMode="discrete"/>'
        f'</rect>'
    )
    return rect
