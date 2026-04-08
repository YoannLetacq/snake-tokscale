"""Snake path generation over the grid.

The snake traverses every cell in a boustrophedon (zigzag) sweep: across the
first column top-to-bottom, across the second column bottom-to-top, and so on.
This always produces a valid non-self-intersecting Hamiltonian path on a
``weeks × rows`` rectangular grid without any pathfinding.
"""

from __future__ import annotations

Coord = tuple[int, int]


def build_snake_path(weeks: int, rows: int) -> list[Coord]:
    """Return a zigzag path visiting every cell of a ``weeks × rows`` grid."""
    if weeks <= 0 or rows <= 0:
        raise ValueError("weeks and rows must be positive")

    path: list[Coord] = []
    for col in range(weeks):
        if col % 2 == 0:
            row_iter = range(rows)
        else:
            row_iter = range(rows - 1, -1, -1)
        path.extend((col, row) for row in row_iter)
    return path
