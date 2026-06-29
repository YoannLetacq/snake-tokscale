"""Snake path generation over the grid.

The snake follows a randomized Hamiltonian path built with a Warnsdorff-guided
depth-first search. It starts from a random cell and, at each step, walks to
an adjacent unvisited cell with the fewest onward moves (the Warnsdorff rule,
which is what makes the Hamiltonian search converge). Ties on that primary
score are broken by *Manhattan distance to the nearest uneaten marker* so the
snake actively hunts food instead of wandering off, and remaining ties are
broken randomly for varied trajectories.

This guarantees:

- no self-crossing (each cell is visited exactly once),
- full coverage of the grid whenever a Hamiltonian path exists,
- a different spawn point and varied, human-looking trajectories on every run,
- a preference for heading toward the closest marker.
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass, field

from snake_tokscale.normalize import Cell

Coord = tuple[int, int]


@dataclass(frozen=True)
class _GridDims:
    """Immutable grid dimensions derived once per path-finding run."""

    weeks: int
    rows: int
    total: int


@dataclass
class _DfsState:
    """Mutable state passed through the Hamiltonian DFS recursion."""

    dims: _GridDims
    rng: random.Random
    path: list[Coord] = field(default_factory=list)
    visited: set[Coord] = field(default_factory=set)
    remaining_markers: set[Coord] = field(default_factory=set)
    budget: int = 0


class _BudgetExhausted(Exception):
    """Raised when an attempt exceeds its DFS step budget."""


_DIRECTIONS: tuple[tuple[int, int], ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))


def build_snake_path(
    weeks: int,
    rows: int,
    cells: list[Cell],
    seed: int | None = None,
    max_steps: int = 500,
) -> tuple[list[Coord], list[int]]:
    """Return a randomized Hamiltonian path and its marker-hit indices.

    ``seed`` makes the result deterministic (used by tests). When ``seed`` is
    ``None`` the system RNG is used, so each SVG regeneration yields a new
    spawn point and trajectory. ``max_steps`` is reserved for API stability.
    """
    _ = max_steps  # reserved for API compatibility
    if weeks <= 0 or rows <= 0:
        raise ValueError("weeks and rows must be positive")

    rng = random.Random(seed)
    markers = _marker_positions(cells, rows)

    path = _find_hamiltonian_path(weeks, rows, rng, markers)
    if path is None:
        # Safety net: should be unreachable on realistic grid sizes, but keeps
        # the pipeline alive if Warnsdorff fails to converge.
        path = _boustrophedon(weeks, rows)

    hits: list[int] = []
    for step, (col, row) in enumerate(path):
        cell_idx = col * rows + row
        if 0 <= cell_idx < len(cells) and cells[cell_idx].get("level", 0) > 0:
            hits.append(step)

    return path, hits


def _marker_positions(cells: list[Cell], rows: int) -> set[Coord]:
    """Return ``(col, row)`` of every cell whose level indicates a marker."""
    markers: set[Coord] = set()
    for idx, cell in enumerate(cells):
        if cell.get("level", 0) > 0:
            markers.add((idx // rows, idx % rows))
    return markers


def _majority_parity(weeks: int, rows: int) -> int | None:
    """Return the ``(col + row) % 2`` parity that holds more cells.

    On a bipartite grid, a Hamiltonian path can only start on the majority
    colour when the two colour classes differ in size (e.g. odd×odd grids).
    Returns ``None`` when the colours are balanced (any start is valid).
    """
    black = 0
    white = 0
    for col in range(weeks):
        for row in range(rows):
            if (col + row) % 2 == 0:
                black += 1
            else:
                white += 1
    if black == white:
        return None
    return 0 if black > white else 1


def _find_hamiltonian_path(
    weeks: int,
    rows: int,
    rng: random.Random,
    markers: set[Coord],
    attempts: int = 24,
) -> list[Coord] | None:
    """Try several random starts; each attempt runs a budgeted Warnsdorff DFS.

    Each attempt has a step budget so a single pathological RNG state cannot
    stall the whole build. If every bounded attempt fails, the caller falls
    back to a deterministic boustrophedon so the pipeline always terminates.
    """
    total = weeks * rows
    majority_parity = _majority_parity(weeks, rows)
    # Generous per-attempt budget: ~50× the cell count is enough for even
    # noisy Warnsdorff runs on a 53×7 grid while finishing in milliseconds.
    per_attempt_budget = max(total * 50, 5000)
    prev_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(prev_limit, total + 200))
    try:
        tried = 0
        while tried < attempts:
            start_col = rng.randrange(weeks)
            start_row = rng.randrange(rows)
            if (
                majority_parity is not None
                and (start_col + start_row) % 2 != majority_parity
            ):
                continue  # wrong bipartite class — no Ham path from here
            tried += 1
            start: Coord = (start_col, start_row)
            remaining = set(markers)
            remaining.discard(start)  # spawning on a marker already eats it
            state = _DfsState(
                dims=_GridDims(weeks=weeks, rows=rows, total=total),
                rng=rng,
                path=[start],
                visited={start},
                remaining_markers=remaining,
                budget=per_attempt_budget,
            )
            try:
                if _dfs(state):
                    return state.path
            except _BudgetExhausted:
                continue  # this start blew its budget — try another
        return None
    finally:
        sys.setrecursionlimit(prev_limit)


def _dfs(state: _DfsState) -> bool:
    """Warnsdorff DFS, tie-broken by distance to the nearest uneaten marker."""
    if len(state.path) == state.dims.total:
        return True
    state.budget -= 1
    if state.budget <= 0:
        raise _BudgetExhausted()
    col, row = state.path[-1]
    candidates: list[tuple[int, int, Coord]] = []
    for delta_col, delta_row in _DIRECTIONS:
        nxt = (col + delta_col, row + delta_row)
        if (
            0 <= nxt[0] < state.dims.weeks
            and 0 <= nxt[1] < state.dims.rows
            and nxt not in state.visited
        ):
            degree = _unvisited_degree(nxt, state)
            hunger = _nearest_marker_distance(nxt, state)
            candidates.append((degree, hunger, nxt))
    if not candidates:
        return False
    # Random shuffle first so cells that tie on both scores are picked
    # varietly; stable sort then preserves the (degree, hunger) ranking.
    state.rng.shuffle(candidates)
    candidates.sort(key=lambda item: (item[0], item[1]))
    for _deg, _hunger, nxt in candidates:
        state.visited.add(nxt)
        state.path.append(nxt)
        marker_eaten = nxt in state.remaining_markers
        if marker_eaten:
            state.remaining_markers.discard(nxt)
        if _dfs(state):
            return True
        if marker_eaten:
            state.remaining_markers.add(nxt)
        state.visited.remove(nxt)
        state.path.pop()
    return False


def _nearest_marker_distance(cell: Coord, state: _DfsState) -> int:
    """Manhattan distance from ``cell`` to the closest remaining marker."""
    if not state.remaining_markers:
        return 0
    col, row = cell
    return min(
        abs(col - mc) + abs(row - mr) for mc, mr in state.remaining_markers
    )


def _unvisited_degree(cell: Coord, state: _DfsState) -> int:
    """Count adjacent, in-bounds, unvisited neighbours of ``cell``."""
    count = 0
    col, row = cell
    for delta_col, delta_row in _DIRECTIONS:
        next_col, next_row = col + delta_col, row + delta_row
        if (
            0 <= next_col < state.dims.weeks
            and 0 <= next_row < state.dims.rows
            and (next_col, next_row) not in state.visited
        ):
            count += 1
    return count


def _boustrophedon(weeks: int, rows: int) -> list[Coord]:
    """Deterministic zig-zag fallback used only if the DFS cannot converge."""
    path: list[Coord] = []
    for col in range(weeks):
        row_range = range(rows) if col % 2 == 0 else range(rows - 1, -1, -1)
        for row in row_range:
            path.append((col, row))
    return path
