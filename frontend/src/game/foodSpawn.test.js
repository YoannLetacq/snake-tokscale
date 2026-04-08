import { describe, expect, it } from 'vitest'
import { spawnFood } from './foodSpawn.js'

describe('spawnFood', () => {
  it('never returns a cell occupied by the snake', () => {
    const snake = [
      { x: 0, y: 0 },
      { x: 0, y: 1 },
      { x: 0, y: 2 },
    ]
    const rng = mulberry32(42)
    for (let i = 0; i < 500; i += 1) {
      const food = spawnFood(5, snake, rng)
      expect(snake.every((c) => !(c.x === food.x && c.y === food.y))).toBe(true)
    }
  })

  it('returns null when the grid is full', () => {
    const snake = []
    for (let x = 0; x < 2; x += 1) {
      for (let y = 0; y < 7; y += 1) {
        snake.push({ x, y })
      }
    }
    expect(spawnFood(2, snake)).toBeNull()
  })

  it('falls back to linear scan if rng keeps colliding', () => {
    const snake = [{ x: 0, y: 0 }]
    const stuckRng = () => 0 // always picks index 0 → (0,0), which is occupied
    const food = spawnFood(3, snake, stuckRng)
    expect(food).not.toBeNull()
    expect(food).not.toEqual({ x: 0, y: 0 })
  })
})

// Small deterministic RNG for test reproducibility.
function mulberry32(seed) {
  let a = seed
  return function () {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
