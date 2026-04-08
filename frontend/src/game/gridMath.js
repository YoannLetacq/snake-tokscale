// Grid math helpers for the snake game. Pure functions — no React, no state.
// The grid is `weeks` columns (x) × 7 rows (y). x=0 is the leftmost column,
// y=0 is Sunday (top). Cells are addressed as `{ x, y }`.

export const ROWS = 7

export function indexOf(weeks, x, y) {
  return x * ROWS + y
}

export function coordOf(weeks, index) {
  return { x: Math.floor(index / ROWS), y: index % ROWS }
}

export function inBounds(weeks, { x, y }) {
  return x >= 0 && x < weeks && y >= 0 && y < ROWS
}

export function equal(a, b) {
  return a.x === b.x && a.y === b.y
}

export function move(head, direction) {
  switch (direction) {
    case 'UP':
      return { x: head.x, y: head.y - 1 }
    case 'DOWN':
      return { x: head.x, y: head.y + 1 }
    case 'LEFT':
      return { x: head.x - 1, y: head.y }
    case 'RIGHT':
      return { x: head.x + 1, y: head.y }
    default:
      return head
  }
}

export function isOpposite(a, b) {
  return (
    (a === 'UP' && b === 'DOWN') ||
    (a === 'DOWN' && b === 'UP') ||
    (a === 'LEFT' && b === 'RIGHT') ||
    (a === 'RIGHT' && b === 'LEFT')
  )
}
