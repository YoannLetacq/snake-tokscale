import { ROWS } from './gridMath.js'

// Pick a uniformly-random cell that is not occupied by the snake. Deterministic
// when a `rng` function is supplied (injected in tests).
export function spawnFood(weeks, snake, rng = Math.random) {
  const occupied = new Set(snake.map((c) => `${c.x},${c.y}`))
  const total = weeks * ROWS
  if (occupied.size >= total) {
    return null
  }
  // Reservoir / rejection sample — grid is tiny (371 cells) so rejection is
  // effectively O(1) amortised for any realistic snake length.
  for (let attempt = 0; attempt < 1000; attempt += 1) {
    const idx = Math.floor(rng() * total)
    const x = Math.floor(idx / ROWS)
    const y = idx % ROWS
    if (!occupied.has(`${x},${y}`)) {
      return { x, y }
    }
  }
  // Fallback: linear scan — guarantees correctness if rng is pathological.
  for (let x = 0; x < weeks; x += 1) {
    for (let y = 0; y < ROWS; y += 1) {
      if (!occupied.has(`${x},${y}`)) return { x, y }
    }
  }
  return null
}
