import { ROWS, equal, inBounds, isOpposite, move } from './gridMath.js'

// Game state machine:
//   IDLE  --START-->   PLAYING
//   PLAYING --collision--> LOST
//   PLAYING --all cells eaten--> WON
//   LOST / WON --START--> PLAYING

const INITIAL_DIRECTION = 'RIGHT'
const INITIAL_SNAKE_LENGTH = 3

export const STATUS = {
  IDLE: 'IDLE',
  PLAYING: 'PLAYING',
  LOST: 'LOST',
  WON: 'WON',
}

export function createInitialState({ weeks, winScore, best = 0, cells = [] } = {}) {
  return {
    status: STATUS.IDLE,
    weeks,
    winScore,
    snake: [],
    dir: INITIAL_DIRECTION,
    pendingDir: INITIAL_DIRECTION,
    cells: [...cells], // The heatmap itself is the game map
    score: 0,
    best,
  }
}

function startingSnake(weeks) {
  const midX = Math.floor(weeks / 2)
  const midY = Math.floor(ROWS / 2)
  const snake = []
  for (let i = 0; i < INITIAL_SNAKE_LENGTH; i += 1) {
    snake.unshift({ x: midX - i, y: midY })
  }
  return snake
}

export function gameReducer(state, action) {
  switch (action.type) {
    case 'START':
      return startGame(state, action)
    case 'CHANGE_DIR':
      return changeDir(state, action)
    case 'TICK':
      return tick(state, action)
    case 'RESET':
      return createInitialState({
        weeks: state.weeks,
        winScore: state.winScore,
        best: state.best,
        cells: state.cells, // Use original if possible, but START will overwrite
      })
    default:
      return state
  }
}

function startGame(state, action) {
  const snake = startingSnake(state.weeks)
  const cells = action.cells ? [...action.cells] : [...state.cells]
  // Refresh winScore from the action when provided. The host component
  // computes it from the freshly loaded grid.json — without this, the
  // reducer would keep the stale 0 captured at first mount (when grid.json
  // had not yet arrived) and the win check could never fire.
  const winScore = action.winScore ?? state.winScore
  return {
    ...state,
    status: STATUS.PLAYING,
    snake,
    dir: INITIAL_DIRECTION,
    pendingDir: INITIAL_DIRECTION,
    cells,
    score: 0,
    winScore,
  }
}

function changeDir(state, action) {
  if (state.status !== STATUS.PLAYING) return state
  const next = action.direction
  if (isOpposite(state.dir, next)) return state
  return { ...state, pendingDir: next }
}

function tick(state) {
  if (state.status !== STATUS.PLAYING) return state
  const dir = state.pendingDir
  const head = move(state.snake[state.snake.length - 1], dir)

  if (!inBounds(state.weeks, head)) {
    return loseGame(state)
  }

  // Check if head is on a contribution marker
  const cellIdx = head.x * ROWS + head.y
  const cell = state.cells[cellIdx]
  const eating = cell && cell.level > 0

  // Self-collision: new head hits any body cell that will remain on the board
  // on the next tick. The tail moves away unless we're eating, so the last
  // body cell can be re-occupied except when we grow.
  const body = eating ? state.snake : state.snake.slice(1)
  if (body.some((c) => equal(c, head))) {
    return loseGame(state)
  }

  const snake = eating ? [...state.snake, head] : [...state.snake.slice(1), head]
  const score = eating ? state.score + 1 : state.score
  
  let cells = state.cells
  if (eating) {
    cells = [...state.cells]
    cells[cellIdx] = { ...cell, level: 0, tokens: 0 }
  }

  // Win condition: every marker has been eaten. We also require that the
  // game actually had markers to start with — otherwise an all-level-0
  // board (e.g. the fallback grid before grid.json loads) would instantly
  // satisfy the predicate and lock the player on the WON screen.
  const win = state.winScore > 0 && cells.every((c) => c.level === 0)

  if (win) {
    return {
      ...state,
      status: STATUS.WON,
      dir,
      pendingDir: dir,
      snake,
      cells,
      score,
      best: Math.max(state.best, score),
    }
  }

  return {
    ...state,
    dir,
    pendingDir: dir,
    snake,
    cells,
    score,
  }
}

function loseGame(state) {
  return {
    ...state,
    status: STATUS.LOST,
    best: Math.max(state.best, state.score),
  }
}
