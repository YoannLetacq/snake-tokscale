import { describe, expect, it } from 'vitest'
import { coordOf, equal, inBounds, indexOf, isOpposite, move } from './gridMath.js'

describe('gridMath', () => {
  it('indexOf and coordOf are inverses', () => {
    for (let x = 0; x < 10; x += 1) {
      for (let y = 0; y < 7; y += 1) {
        const i = indexOf(10, x, y)
        expect(coordOf(10, i)).toEqual({ x, y })
      }
    }
  })

  it('inBounds rejects out-of-grid coordinates', () => {
    expect(inBounds(10, { x: 0, y: 0 })).toBe(true)
    expect(inBounds(10, { x: 9, y: 6 })).toBe(true)
    expect(inBounds(10, { x: -1, y: 0 })).toBe(false)
    expect(inBounds(10, { x: 10, y: 0 })).toBe(false)
    expect(inBounds(10, { x: 0, y: 7 })).toBe(false)
  })

  it('move advances one cell in each direction', () => {
    const h = { x: 5, y: 3 }
    expect(move(h, 'UP')).toEqual({ x: 5, y: 2 })
    expect(move(h, 'DOWN')).toEqual({ x: 5, y: 4 })
    expect(move(h, 'LEFT')).toEqual({ x: 4, y: 3 })
    expect(move(h, 'RIGHT')).toEqual({ x: 6, y: 3 })
  })

  it('equal compares coordinates', () => {
    expect(equal({ x: 1, y: 2 }, { x: 1, y: 2 })).toBe(true)
    expect(equal({ x: 1, y: 2 }, { x: 2, y: 1 })).toBe(false)
  })

  it('isOpposite detects 180° reversals', () => {
    expect(isOpposite('UP', 'DOWN')).toBe(true)
    expect(isOpposite('LEFT', 'RIGHT')).toBe(true)
    expect(isOpposite('UP', 'LEFT')).toBe(false)
  })
})
