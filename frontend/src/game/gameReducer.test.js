import { describe, expect, it } from 'vitest'
import { STATUS, createInitialState, gameReducer } from './gameReducer.js'
import { ROWS } from './gridMath.js'

const baseWeeks = 10
const baseConfig = { weeks: baseWeeks, winScore: 3 }

function createMockCells(weeks, markers = []) {
  const cells = Array.from({ length: weeks * ROWS }, (_, i) => ({
    date: '2024-01-01',
    tokens: 0,
    level: 0,
    key: i,
  }))
  markers.forEach(({ x, y, level = 1 }) => {
    cells[x * ROWS + y] = { ...cells[x * ROWS + y], level }
  })
  return cells
}

function init(cells = []) {
  const actualCells = cells.length > 0 ? cells : createMockCells(baseWeeks)
  return createInitialState({ ...baseConfig, cells: actualCells })
}

describe('gameReducer', () => {
  it('starts in IDLE with no snake', () => {
    const state = init()
    expect(state.status).toBe(STATUS.IDLE)
    expect(state.snake).toEqual([])
    expect(state.score).toBe(0)
  })

  it('START transitions to PLAYING and spawns snake', () => {
    const state = gameReducer(init(), { type: 'START' })
    expect(state.status).toBe(STATUS.PLAYING)
    expect(state.snake.length).toBe(3)
  })

  it('TICK moves the snake one cell in current direction', () => {
    const started = gameReducer(init(), { type: 'START' })
    const before = started.snake[started.snake.length - 1]
    const after = gameReducer(started, { type: 'TICK' })
    const newHead = after.snake[after.snake.length - 1]
    expect(newHead.x).toBe(before.x + 1)
    expect(newHead.y).toBe(before.y)
  })

  it('CHANGE_DIR rejects 180° reverse', () => {
    const started = gameReducer(init(), { type: 'START' })
    const changed = gameReducer(started, { type: 'CHANGE_DIR', direction: 'LEFT' })
    expect(changed.pendingDir).toBe(started.dir)
  })

  it('CHANGE_DIR accepts perpendicular directions', () => {
    const started = gameReducer(init(), { type: 'START' })
    const changed = gameReducer(started, { type: 'CHANGE_DIR', direction: 'UP' })
    expect(changed.pendingDir).toBe('UP')
  })

  it('wall collision → LOST', () => {
    // Fill all cells with 1 marker to avoid early WON
    const cells = createMockCells(baseWeeks, [{ x: 9, y: 0 }])
    let state = gameReducer(init(cells), { type: 'START' })
    for (let i = 0; i < 100; i += 1) {
      state = gameReducer(state, { type: 'TICK' })
      if (state.status === STATUS.LOST) break
    }
    expect(state.status).toBe(STATUS.LOST)
    expect(state.best).toBeGreaterThanOrEqual(0)
  })

  it('eating marker grows snake and increments score', () => {
    const started = gameReducer(init(), { type: 'START' })
    const head = started.snake[started.snake.length - 1]
    // Place a marker right in front of the head
    const markerPos = { x: head.x + 1, y: head.y }
    const cellsWithMarker = createMockCells(baseWeeks, [markerPos, { x: 0, y: 0 }])
    
    let state = gameReducer(init(cellsWithMarker), { type: 'START' })
    const before = state.snake.length
    
    state = gameReducer(state, { type: 'TICK' })
    expect(state.snake.length).toBe(before + 1)
    expect(state.score).toBe(1)
    expect(state.cells[markerPos.x * ROWS + markerPos.y].level).toBe(0)
  })

  it('eating all markers → WON', () => {
    const started = gameReducer(init(), { type: 'START' })
    const head = started.snake[started.snake.length - 1]
    // Only ONE marker in the whole grid, right in front of head
    const markerPos = { x: head.x + 1, y: head.y }
    const cells = createMockCells(baseWeeks, [markerPos])
    
    let state = gameReducer(init(cells), { type: 'START' })
    state = gameReducer(state, { type: 'TICK' })
    
    expect(state.status).toBe(STATUS.WON)
    expect(state.best).toBe(1)
  })

  it('does not instant-win when started with a zero-marker fallback grid', () => {
    // Reproduces the production race: the host mounts before grid.json
    // has loaded, so winScore is captured as 0 and cells are all level 0.
    // The reducer must not transition straight to WON on the first tick.
    const fallback = createMockCells(baseWeeks)
    const initial = createInitialState({ weeks: baseWeeks, winScore: 0, cells: fallback })
    let state = gameReducer(initial, { type: 'START' })
    state = gameReducer(state, { type: 'TICK' })
    expect(state.status).toBe(STATUS.PLAYING)
  })

  it('START refreshes winScore from the action payload', () => {
    // The host re-dispatches START with the real winScore once grid.json
    // arrives — the reducer state must pick it up so wins become possible.
    const fallback = createMockCells(baseWeeks)
    const initial = createInitialState({ weeks: baseWeeks, winScore: 0, cells: fallback })
    const real = createMockCells(baseWeeks, [{ x: 5, y: 3 }, { x: 6, y: 3 }])
    const started = gameReducer(initial, { type: 'START', cells: real, winScore: 2 })
    expect(started.winScore).toBe(2)
    expect(started.status).toBe(STATUS.PLAYING)
  })

  it('RESET returns to IDLE but preserves best', () => {
    let state = gameReducer(init(), { type: 'START' })
    state = { ...state, best: 7 }
    const reset = gameReducer(state, { type: 'RESET' })
    expect(reset.status).toBe(STATUS.IDLE)
    expect(reset.best).toBe(7)
  })
})
