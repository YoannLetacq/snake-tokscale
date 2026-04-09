"""Snake path generation over the grid.

The snake follows a randomized greedy path: it tries to move towards the nearest
contribution marker while avoiding its own recent tail. If no markers remain,
it wanders randomly.
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
    """Return a path and a list of step indices where markers were eaten."""
    if weeks <= 0 or rows <= 0:
        raise ValueError("weeks and rows must be positive")

    rng = random.Random(seed)
    markers = _extract_markers(cells, rows)

    if not markers:
        return [(0, 0)], []

    start = _pick_start_pos(markers, rows, rng)
    path = [start]
    visited = {start} if start in markers else set()
    hits = [0] if start in markers else []

    curr = start
    for step in range(1, max_steps):
        targets = markers - visited
        if not targets:
            break

        neighbors = _get_neighbors(curr, weeks, rows, path)
        if not neighbors:
            break

        curr = _pick_best_neighbor(neighbors, targets, rng)
        path.append(curr)

        if curr in markers:
            visited.add(curr)
            hits.append(step)

    return path, hits


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


def _get_neighbors(curr: Coord, weeks: int, rows: int, path: list[Coord]) -> list[Coord]:
    neighbors = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = curr[0] + dx, curr[1] + dy
        if 0 <= nx < weeks and 0 <= ny < rows:
            if len(path) > 1 and (nx, ny) == path[-2]:
                continue
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
