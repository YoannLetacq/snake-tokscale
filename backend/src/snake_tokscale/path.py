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
    max_steps: int = 200,
) -> list[Coord]:
    """Return a randomized greedy path visiting markers on a ``weeks × rows`` grid."""
    if weeks <= 0 or rows <= 0:
        raise ValueError("weeks and rows must be positive")

    rng = random.Random(seed)
    
    # Identify target markers
    markers = set()
    for idx, cell in enumerate(cells):
        if cell.get("level", 0) > 0:
            col = idx // rows
            row = idx % rows
            markers.add((col, row))

    # Start at a random edge or a marker if none
    if markers:
        start = rng.choice(list(markers))
    else:
        start = (0, 0)

    path = [start]
    visited_markers = set()
    if start in markers:
        visited_markers.add(start)

    curr = start
    for _ in range(max_steps):
        # Remaining targets
        targets = markers - visited_markers
        
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = curr[0] + dx, curr[1] + dy
            if 0 <= nx < weeks and 0 <= ny < rows:
                # Avoid immediate backtracking (simple heuristic)
                if len(path) > 1 and (nx, ny) == path[-2]:
                    continue
                neighbors.append((nx, ny))

        if not neighbors:
            break

        # Score neighbors: closer to nearest target is better
        scored = []
        for n in neighbors:
            score = 0
            if targets:
                # Manhattan distance to nearest target
                dist = min(abs(n[0] - t[0]) + abs(n[1] - t[1]) for t in targets)
                score -= dist * 10
            
            # Add a bit of randomness to break ties and make it "alive"
            score += rng.random() * 5
            scored.append((score, n))

        # Pick best neighbor
        scored.sort(key=lambda x: x[0], reverse=True)
        curr = scored[0][1]
        
        path.append(curr)
        if curr in markers:
            visited_markers.add(curr)
            
        # If all markers eaten, we can stop or keep wandering. 
        # User said "attract by markers", so if none left, we stop.
        if not targets and curr in markers:
            # Add a few extra steps to show it leaving the last marker
            pass

    return path
