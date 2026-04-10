"""Render an animated snake SVG that traverses the tokscale heatmap.

The output uses SMIL ``<animate>`` tags. The snake follows a randomized
Hamiltonian path (see :mod:`snake_tokscale.path`) that spawns at a random
cell and never crosses itself, while still clearing every marker and winning.
"""

from __future__ import annotations

from snake_tokscale.normalize import Cell
from snake_tokscale.path import build_snake_path
from snake_tokscale.svg import (
    CELL_GAP,
    CELL_SIZE,
    ROWS,
    Palette,
    get_random_palette,
    iter_cell_positions,
    svg_header,
)

BACKGROUND_COLOR = "#0d1117"


def render_animated_snake(
    cells: list[Cell],
    weeks: int,
    snake_length: int = 4,
    _duration_s: float = 30.0,
    palette: Palette | None = None,
) -> tuple[str, Palette]:
    """Return ``(svg_string, palette)`` for an animated snake traversal."""
    if snake_length <= 0:
        raise ValueError("snake_length must be positive")
    expected = weeks * ROWS
    if len(cells) != expected:
        raise ValueError(f"expected {expected} cells for {weeks} weeks, got {len(cells)}")

    # Randomized Hamiltonian path (spawn is random, snake hunts markers)
    path, hits = build_snake_path(weeks=weeks, rows=ROWS, cells=cells)

    # Truncate the loop so the snake stops as soon as it has eaten every
    # marker — no more pointless wandering across empty cells after the
    # last meal. If there are no markers we just keep the full sweep.
    if hits:
        stop_step = max(hits) + 1
        path = path[:stop_step]

    # Color palette for this build
    if palette is None:
        palette = get_random_palette()

    # ~0.1s per step for a snappy animation
    actual_duration = len(path) * 0.1

    parts = svg_header(
        weeks, cells=cells, background=BACKGROUND_COLOR, palette_name=palette.name
    )

    # Global loop sync
    loop_anim = (
        f'<rect width="0" height="0">'
        f'<animate id="loop" attributeName="opacity" from="1" to="1" '
        f'dur="{actual_duration:.4f}s" repeatCount="indefinite"/>'
        f'</rect>'
    )
    parts.append(loop_anim)

    parts.extend(_render_cells(cells, path, palette, actual_duration))
    parts.extend(_render_snake(path, hits, palette, actual_duration))
    parts.append("</g></svg>")
    return "".join(parts), palette


def _render_cells(
    cells: list[Cell],
    path: list[tuple[int, int]],
    palette: Palette,
    duration_s: float,
) -> list[str]:
    """Emit heatmap cells with fade-out animations on head contact."""
    path_index = _build_path_index(path)
    pieces: list[str] = []

    for col, row, x, y, level, color in iter_cell_positions(cells, palette):
        rect = (
            f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2" ry="2" fill="{color}">'
        )
        if level > 0 and (col, row) in path_index:
            idx = path_index[(col, row)]
            fade = _fade_animation(
                idx, len(path), color, palette.levels[0], duration_s
            )
            rect += fade
        rect += "</rect>"
        pieces.append(rect)

    return pieces


def _build_path_index(path: list[tuple[int, int]]) -> dict[tuple[int, int], int]:
    index = {}
    for i, coord in enumerate(path):
        if coord not in index:
            index[coord] = i
    return index


def _fade_animation(
    step: int,
    steps: int,
    from_color: str,
    to_color: str,
    dur: float,
) -> str:
    """Fade a cell color once the head reaches it."""
    when = min(max(step / max(steps - 1, 1), 0.0001), 0.9999)
    step_pct = 1.0 / steps
    end_pct = min(when + step_pct * 2, 1.0)

    return (
        f'<animate attributeName="fill" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite" '
        f'calcMode="linear" fill="freeze" '
        f'keyTimes="0;{when:.4f};{end_pct:.4f};1" '
        f'values="{from_color};{from_color};{to_color};{to_color}"/>'
    )


TAPER_COUNT = 5
TAIL_SHRINK = 5


def _seg_geometry(seg_idx: int, max_segments: int) -> tuple[int, float, int]:
    """Return ``(size, offset, rx)`` for a segment.

    Head (index 0) extends beyond the cell; the last *TAPER_COUNT* body
    segments shrink progressively toward the tail tip.
    """
    if seg_idx == 0:
        size = CELL_SIZE + 2
        offset = -(size - CELL_SIZE) / 2
        return size, offset, 4

    body_size = CELL_SIZE - 2
    body_offset = (CELL_SIZE - body_size) / 2          # 1px inset

    from_tail = max_segments - 1 - seg_idx
    if from_tail < TAPER_COUNT:
        shrink = TAIL_SHRINK - from_tail
        return body_size - shrink, body_offset + shrink / 2, 2
    return body_size, body_offset, 3


def _render_snake(
    path: list[tuple[int, int]],
    hits: list[int],
    palette: Palette,
    duration_s: float,
) -> list[str]:
    """Emit growing snake segments following the fixed path."""
    pieces: list[str] = []
    # Initial length 4 + grow by 1 for each hit marker
    appearance_steps = [0, 0, 0, 0] + hits
    max_segments = min(len(appearance_steps), 60)

    data = {
        "path": path,
        "max_segments": max_segments,
        "steps": len(path),
        "duration": duration_s,
        "palette": palette,
    }

    for seg_idx in range(max_segments):
        start_step = appearance_steps[seg_idx]
        pieces.append(_render_segment(seg_idx, start_step, data))

    return pieces


def _get_shifted_coords(
    seg_idx: int, steps: int, data: dict, offset: float,
) -> tuple[str, str]:
    """Calculate the semicolon-separated coordinate strings for a segment."""
    path = data["path"]
    step = CELL_SIZE + CELL_GAP
    shifted_x: list[str] = []
    shifted_y: list[str] = []
    for i in range(steps):
        lag_idx = max(0, i - seg_idx)
        col, row = path[lag_idx]
        shifted_x.append(f"{col * step + offset:.1f}")
        shifted_y.append(f"{row * step + offset:.1f}")
    return ";".join(shifted_x), ";".join(shifted_y)


def _init_pos(path: list[tuple[int, int]], offset: float) -> tuple[float, float]:
    """Return the initial pixel ``(x, y)`` for a segment."""
    col, row = path[0]
    pitch = CELL_SIZE + CELL_GAP
    return col * pitch + offset, row * pitch + offset


def _render_segment(seg_idx: int, start_step: int, data: dict) -> str:
    """Render one segment with lag-logic and opacity sync."""
    steps, dur = data["steps"], data["duration"]
    size, offset, rx = _seg_geometry(seg_idx, data["max_segments"])
    x_v, y_v = _get_shifted_coords(seg_idx, steps, data, offset)

    color = data["palette"].head if seg_idx == 0 else data["palette"].snake
    s_pct = start_step / max(steps - 1, 1)
    ix, iy = _init_pos(data["path"], offset)

    rect = (
        f'<rect class="snake-segment" width="{size}" height="{size}" '
        f'rx="{rx}" ry="{rx}" fill="{color}" x="{ix:.1f}" y="{iy:.1f}">'
    )

    if seg_idx >= 4:
        rect += (
            f'<animate attributeName="opacity" values="0;0;1;1" '
            f'keyTimes="0;{s_pct:.4f};{s_pct:.4f};1" '
            f'begin="loop.begin" dur="{dur:.4f}s" '
            f'repeatCount="indefinite"/>'
        )
    else:
        rect += (
            f'<animate attributeName="opacity" from="1" to="1" '
            f'begin="loop.begin" dur="{dur:.4f}s" '
            f'repeatCount="indefinite"/>'
        )

    rect += (
        f'<animate attributeName="x" values="{x_v}" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite" '
        f'calcMode="discrete"/>'
        f'<animate attributeName="y" values="{y_v}" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite" '
        f'calcMode="discrete"/>'
        f'</rect>'
    )
    return rect
