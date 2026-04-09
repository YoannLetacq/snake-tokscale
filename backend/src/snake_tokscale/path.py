"""Snake path generation over the grid.

The snake follows a randomized Hamiltonian path built with a Warnsdorff-guided
depth-first search: it starts from a random cell and, at each step, walks to
an adjacent unvisited cell with the fewest onward moves (ties broken
randomly). This guarantees:

- no self-crossing (each cell is visited exactly once),
- full coverage of the grid whenever a Hamiltonian path exists,
- a different spawn point and varied, human-looking trajectories on every run.
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass, field

from snake_tokscale.normalize import Cell

Coord = tuple[int, int]


@dataclass
class _DfsState:
    """Mutable state passed through the Hamiltonian DFS recursion."""

    weeks: int
    rows: int
    total: int
    rng: random.Random
    path: list[Coord] = field(default_factory=list)
    visited: set[Coord] = field(default_factory=set)

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
    majority_parity = _majority_parity(weeks, rows)

    path = _find_hamiltonian_path(weeks, rows, rng, majority_parity)
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
    majority_parity: int | None,
    attempts: int = 24,
) -> list[Coord] | None:
    """Try several random starts; each attempt runs Warnsdorff-guided DFS."""
    total = weeks * rows
    # Ensure the recursion depth can accommodate the DFS for this grid.
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
            state = _DfsState(
                weeks=weeks,
                rows=rows,
                total=total,
                rng=rng,
                path=[start],
                visited={start},
            )
            if _dfs(state):
                return state.path
        return None
    finally:
        sys.setrecursionlimit(prev_limit)


def _dfs(state: _DfsState) -> bool:
    """Warnsdorff-guided DFS: prefer neighbours with the fewest onward moves."""
    if len(state.path) == state.total:
        return True
    col, row = state.path[-1]
    candidates: list[tuple[int, Coord]] = []
    for delta_col, delta_row in _DIRECTIONS:
        nxt = (col + delta_col, row + delta_row)
        if (
            0 <= nxt[0] < state.weeks
            and 0 <= nxt[1] < state.rows
            and nxt not in state.visited
        ):
            candidates.append((_unvisited_degree(nxt, state), nxt))
    if not candidates:
        return False
    # Random tie-break, then stable sort on degree.
    state.rng.shuffle(candidates)
    candidates.sort(key=lambda item: item[0])
    for _deg, nxt in candidates:
        state.visited.add(nxt)
        state.path.append(nxt)
        if _dfs(state):
            return True
        state.visited.remove(nxt)
        state.path.pop()
    return False


def _unvisited_degree(cell: Coord, state: _DfsState) -> int:
    """Count adjacent, in-bounds, unvisited neighbours of ``cell``."""
    count = 0
    col, row = cell
    for delta_col, delta_row in _DIRECTIONS:
        next_col, next_row = col + delta_col, row + delta_row
        if (
            0 <= next_col < state.weeks
            and 0 <= next_row < state.rows
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
