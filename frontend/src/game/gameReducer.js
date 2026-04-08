import { ROWS, equal, inBounds, isOpposite, move } from './gridMath.js'
import { spawnFood } from './foodSpawn.js'

// Game state machine:
//   IDLE  --START-->   PLAYING
//   PLAYING --collision--> LOST
//   PLAYING --score>=winScore--> WON
//   LOST / WON --START--> PLAYING

const INITIAL_DIRECTION = 'RIGHT'
const INITIAL_SNAKE_LENGTH = 3

export const STATUS = {
  IDLE: 'IDLE',
  PLAYING: 'PLAYING',
  LOST: 'LOST',
  WON: 'WON',
}

export function createInitialState({ weeks, winScore, best = 0 } = {}) {
  return {
    status: STATUS.IDLE,
    weeks,
    winScore,
    snake: [],
    dir: INITIAL_DIRECTION,
    pendingDir: INITIAL_DIRECTION,
    food: null,
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
      })
    default:
      return state
  }
}

function startGame(state, action) {
  const snake = startingSnake(state.weeks)
  const rng = action?.rng
  return {
    ...state,
    status: STATUS.PLAYING,
    snake,
    dir: INITIAL_DIRECTION,
    pendingDir: INITIAL_DIRECTION,
    food: spawnFood(state.weeks, snake, rng),
    score: 0,
  }
}

function changeDir(state, action) {
  if (state.status !== STATUS.PLAYING) return state
  const next = action.direction
  if (isOpposite(state.dir, next)) return state
  return { ...state, pendingDir: next }
}

function tick(state, action) {
  if (state.status !== STATUS.PLAYING) return state
  const dir = state.pendingDir
  const head = move(state.snake[state.snake.length - 1], dir)

  if (!inBounds(state.weeks, head)) {
    return loseGame(state)
  }
  // Self-collision: new head hits any body cell that will remain on the board
  // on the next tick. The tail moves away unless we're eating, so the last
  // body cell can be re-occupied except when we grow.
  const eating = state.food && equal(head, state.food)
  const body = eating ? state.snake : state.snake.slice(1)
  if (body.some((c) => equal(c, head))) {
    return loseGame(state)
  }

  const snake = eating ? [...state.snake, head] : [...state.snake.slice(1), head]
  const score = eating ? state.score + 1 : state.score
  const food = eating ? spawnFood(state.weeks, snake, action?.rng) : state.food

  if (score >= state.winScore) {
    return {
      ...state,
      status: STATUS.WON,
      dir,
      pendingDir: dir,
      snake,
      food: null,
      score,
      best: Math.max(state.best, score),
    }
  }

  return {
    ...state,
    dir,
    pendingDir: dir,
    snake,
    food,
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
