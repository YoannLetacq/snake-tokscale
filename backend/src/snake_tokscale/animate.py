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
_BODY_SIZE = CELL_SIZE - 2
_BODY_OFFSET = (CELL_SIZE - _BODY_SIZE) / 2   # 1px inset
_PITCH = CELL_SIZE + CELL_GAP
_HEAD_SIZE = CELL_SIZE + 2
_HEAD_OFFSET = -(_HEAD_SIZE - CELL_SIZE) / 2


def _render_snake(
    path: list[tuple[int, int]],
    hits: list[int],
    palette: Palette,
    duration_s: float,
) -> list[str]:
    """Emit growing snake segments following the fixed path."""
    pieces: list[str] = []
    appearance = [0, 0, 0, 0] + hits
    max_seg = min(len(appearance), 60)

    shrink_table = _build_shrink_table(max_seg, appearance, len(path))

    ctx = {"path": path, "palette": palette, "dur": duration_s}

    for seg_idx in range(max_seg):
        if seg_idx == 0:
            pieces.append(_render_head(ctx))
        else:
            pieces.append(
                _render_body(seg_idx, ctx,
                             appearance[seg_idx], shrink_table[seg_idx])
            )
    return pieces


def _build_shrink_table(
    max_seg: int, appearance: list[int], steps: int,
) -> dict[int, list[int]]:
    """Return ``{seg_idx: [shrink_at_step_0, shrink_at_step_1, …]}``."""
    table: dict[int, list[int]] = {}
    for seg in range(1, max_seg):
        schedule: list[int] = []
        for step in range(steps):
            after = 0
            for k in range(1, TAPER_COUNT + 1):
                j = seg + k
                if j < max_seg and appearance[j] <= step:
                    after += 1
            schedule.append(max(0, TAPER_COUNT - after))
        table[seg] = schedule
    return table


def _render_head(ctx: dict) -> str:
    """Render the oversized head segment."""
    path, pal, dur = ctx["path"], ctx["palette"], ctx["dur"]
    xs: list[str] = []
    ys: list[str] = []
    for col, row in path:
        xs.append(f"{col * _PITCH + _HEAD_OFFSET:.1f}")
        ys.append(f"{row * _PITCH + _HEAD_OFFSET:.1f}")

    return (
        f'<rect class="snake-segment" width="{_HEAD_SIZE}" height="{_HEAD_SIZE}" '
        f'rx="4" ry="4" fill="{pal.head}" x="{xs[0]}" y="{ys[0]}">'
        f'<animate attributeName="opacity" from="1" to="1" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="x" values="{";".join(xs)}" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite" '
        f'calcMode="discrete"/>'
        f'<animate attributeName="y" values="{";".join(ys)}" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite" '
        f'calcMode="discrete"/>'
        f'</rect>'
    )


def _render_body(
    seg_idx: int, ctx: dict,
    start_step: int, shrink_schedule: list[int],
) -> str:
    """Render one body segment whose size evolves with the taper schedule."""
    path, pal, dur = ctx["path"], ctx["palette"], ctx["dur"]
    steps = len(path)
    s_pct = start_step / max(steps - 1, 1)

    xs, ys, sizes = _body_coords(seg_idx, path, shrink_schedule)

    rect = _body_rect(xs[0], ys[0], sizes[0], pal.snake)
    rect += _opacity_anim(seg_idx, s_pct, dur)
    rect += _xy_anim(xs, ys, dur)

    if any(s != sizes[0] for s in sizes):
        rect += _size_anim(sizes, dur)

    rect += "</rect>"
    return rect


def _body_coords(seg_idx, path, shrink_schedule):
    """Build per-step x, y, and size strings for a body segment."""
    xs: list[str] = []
    ys: list[str] = []
    sizes: list[str] = []
    for i, shrink in enumerate(shrink_schedule):
        lag = max(0, i - seg_idx)
        col, row = path[lag]
        off = _BODY_OFFSET + shrink / 2
        xs.append(f"{col * _PITCH + off:.1f}")
        ys.append(f"{row * _PITCH + off:.1f}")
        sizes.append(str(_BODY_SIZE - shrink))
    return xs, ys, sizes


def _body_rect(ix: str, iy: str, init_size: str, color: str) -> str:
    return (
        f'<rect class="snake-segment" width="{init_size}" height="{init_size}" '
        f'rx="2" ry="2" fill="{color}" x="{ix}" y="{iy}">'
    )


def _opacity_anim(seg_idx: int, s_pct: float, dur: float) -> str:
    if seg_idx >= 4:
        return (
            f'<animate attributeName="opacity" values="0;0;1;1" '
            f'keyTimes="0;{s_pct:.4f};{s_pct:.4f};1" '
            f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite"/>'
        )
    return (
        f'<animate attributeName="opacity" from="1" to="1" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite"/>'
    )


def _xy_anim(xs: list[str], ys: list[str], dur: float) -> str:
    return (
        f'<animate attributeName="x" values="{";".join(xs)}" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite" '
        f'calcMode="discrete"/>'
        f'<animate attributeName="y" values="{";".join(ys)}" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite" '
        f'calcMode="discrete"/>'
    )


def _size_anim(sizes: list[str], dur: float) -> str:
    sz_v = ";".join(sizes)
    return (
        f'<animate attributeName="width" values="{sz_v}" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite" '
        f'calcMode="discrete"/>'
        f'<animate attributeName="height" values="{sz_v}" '
        f'begin="loop.begin" dur="{dur:.4f}s" repeatCount="indefinite" '
        f'calcMode="discrete"/>'
    )
