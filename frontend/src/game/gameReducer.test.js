import { describe, expect, it } from 'vitest'
import { STATUS, createInitialState, gameReducer } from './gameReducer.js'

const baseConfig = { weeks: 10, winScore: 3 }
const fixedRng = () => 0.999 // always picks a deterministic corner-ish cell

function init() {
  return createInitialState(baseConfig)
}

describe('gameReducer', () => {
  it('starts in IDLE with no snake', () => {
    const state = init()
    expect(state.status).toBe(STATUS.IDLE)
    expect(state.snake).toEqual([])
    expect(state.score).toBe(0)
  })

  it('START transitions to PLAYING and spawns snake + food', () => {
    const state = gameReducer(init(), { type: 'START', rng: fixedRng })
    expect(state.status).toBe(STATUS.PLAYING)
    expect(state.snake.length).toBe(3)
    expect(state.food).not.toBeNull()
  })

  it('TICK moves the snake one cell in current direction', () => {
    const started = gameReducer(init(), { type: 'START', rng: fixedRng })
    const before = started.snake[started.snake.length - 1]
    const after = gameReducer(started, { type: 'TICK', rng: fixedRng })
    const newHead = after.snake[after.snake.length - 1]
    expect(newHead.x).toBe(before.x + 1)
    expect(newHead.y).toBe(before.y)
  })

  it('CHANGE_DIR rejects 180° reverse', () => {
    const started = gameReducer(init(), { type: 'START', rng: fixedRng })
    const changed = gameReducer(started, { type: 'CHANGE_DIR', direction: 'LEFT' })
    expect(changed.pendingDir).toBe(started.dir)
  })

  it('CHANGE_DIR accepts perpendicular directions', () => {
    const started = gameReducer(init(), { type: 'START', rng: fixedRng })
    const changed = gameReducer(started, { type: 'CHANGE_DIR', direction: 'UP' })
    expect(changed.pendingDir).toBe('UP')
  })

  it('wall collision → LOST', () => {
    let state = gameReducer(init(), { type: 'START', rng: fixedRng })
    for (let i = 0; i < 100; i += 1) {
      state = gameReducer(state, { type: 'TICK', rng: fixedRng })
      if (state.status === STATUS.LOST) break
    }
    expect(state.status).toBe(STATUS.LOST)
    expect(state.best).toBeGreaterThanOrEqual(0)
  })

  it('eating food grows snake and increments score', () => {
    let state = gameReducer(init(), { type: 'START', rng: fixedRng })
    // Force food right in front of the head to make the next tick an eat.
    const head = state.snake[state.snake.length - 1]
    state = { ...state, food: { x: head.x + 1, y: head.y } }
    const before = state.snake.length
    const after = gameReducer(state, { type: 'TICK', rng: fixedRng })
    expect(after.snake.length).toBe(before + 1)
    expect(after.score).toBe(1)
    expect(after.food).not.toBeNull()
  })

  it('reaching winScore → WON', () => {
    let state = gameReducer({ ...init(), winScore: 1 }, { type: 'START', rng: fixedRng })
    const head = state.snake[state.snake.length - 1]
    state = { ...state, food: { x: head.x + 1, y: head.y } }
    state = gameReducer(state, { type: 'TICK', rng: fixedRng })
    expect(state.status).toBe(STATUS.WON)
    expect(state.best).toBe(1)
  })

  it('RESET returns to IDLE but preserves best', () => {
    let state = gameReducer(init(), { type: 'START', rng: fixedRng })
    state = { ...state, best: 7 }
    const reset = gameReducer(state, { type: 'RESET' })
    expect(reset.status).toBe(STATUS.IDLE)
    expect(reset.best).toBe(7)
  })
})
