"""Snake path generation over the grid.

The snake follows a guaranteed Hamiltonian path (zigzag sweep).
"""

from __future__ import annotations

Coord = tuple[int, int]


def build_snake_path(
    weeks: int,
    rows: int,
    cells: list[dict],
    seed: int | None = None,
    max_steps: int = 500,
) -> tuple[list[Coord], list[int]]:
    """Return a boustrophedon path and hit indices.

    The seed and max_steps arguments are accepted for API compatibility.
    """
    _ = (seed, max_steps)  # mark as used
    if weeks <= 0 or rows <= 0:
        raise ValueError("weeks and rows must be positive")

    path: list[Coord] = []
    for col in range(weeks):
        row_range = range(rows) if col % 2 == 0 else range(rows - 1, -1, -1)
        for row in row_range:
            path.append((col, row))

    hits: list[int] = []
    for step, (col, row) in enumerate(path):
        cell_idx = col * rows + row
        if cell_idx < len(cells) and cells[cell_idx].get("level", 0) > 0:
            hits.append(step)

    return path, hits
