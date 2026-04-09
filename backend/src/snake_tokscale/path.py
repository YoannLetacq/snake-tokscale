"""Snake path generation over the grid.

The snake follows a randomized greedy path that prioritizes contribution markers
while strictly avoiding self-collision.
"""

from __future__ import annotations
import random

Coord = tuple[int, int]


def build_snake_path(
    weeks: int,
    rows: int,
    cells: list[dict],
    seed: int | None = None,
    max_steps: int = 500,
) -> tuple[list[Coord], list[int]]:
    """Return a path and hit indices, strictly avoiding self-collision."""
    if weeks <= 0 or rows <= 0:
        raise ValueError("weeks and rows must be positive")

    rng = random.Random(seed)
    markers = _extract_markers(cells, rows)
    if not markers:
        return [(0, 0)], []

    curr = _pick_start_pos(markers, rows, rng)
    # State tracking
    state = {
        "path": [curr],
        "hits": [0] if curr in markers else [],
        "visited": {curr} if curr in markers else set(),
        "len": 5 if curr in markers else 4
    }

    for step in range(1, max_steps):
        targets = markers - state["visited"]
        if not targets:
            break

        body = set(state["path"][-state["len"]:])
        neighbors = _get_safe_neighbors(curr, weeks, rows, body)
        if not neighbors:
            break

        curr = _pick_best_neighbor(neighbors, targets, rng)
        state["path"].append(curr)

        if curr in markers:
            state["visited"].add(curr)
            state["hits"].append(step)
            state["len"] += 1

    return state["path"], state["hits"]


def _pick_start_pos(markers: set[Coord], rows: int, rng: random.Random) -> Coord:
    first_col = min(m[0] for m in markers)
    if first_col > 17:
        return (first_col - 13, rng.randint(0, rows - 1))
    if rng.random() > 0.5:
        return rng.choice(list(markers))
    return (0, rng.randint(0, rows - 1))


def _extract_markers(cells: list[dict], rows: int) -> set[Coord]:
    markers = set()
    for idx, cell in enumerate(cells):
        if cell.get("level", 0) > 0:
            col = idx // rows
            row = idx % rows
            markers.add((col, row))
    return markers


def _get_safe_neighbors(curr: Coord, weeks: int, rows: int, body: set[Coord]) -> list[Coord]:
    neighbors = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = curr[0] + dx, curr[1] + dy
        if 0 <= nx < weeks and 0 <= ny < rows:
            if (nx, ny) not in body:
                neighbors.append((nx, ny))
    return neighbors


def _pick_best_neighbor(
    neighbors: list[Coord],
    targets: set[Coord],
    rng: random.Random,
) -> Coord:
    scored = []
    for n in neighbors:
        score = 0
        if targets:
            dist = min(abs(n[0] - t[0]) + abs(n[1] - t[1]) for t in targets)
            score -= dist * 10
        score += rng.random() * 5
        scored.append((score, n))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]
