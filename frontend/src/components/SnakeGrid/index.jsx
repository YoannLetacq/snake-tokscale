import { useEffect, useMemo, useReducer } from 'react'
import Grid from './Grid.jsx'
import Snake from './Snake.jsx'
import Food from './Food.jsx'
import HUD from './HUD.jsx'
import Overlays from './Overlays.jsx'
import { useGameLoop } from './hooks/useGameLoop.js'
import { useKeyboard } from './hooks/useKeyboard.js'
import { createInitialState, gameReducer } from '../../game/gameReducer.js'
import { CELL_GAP, CELL_SIZE } from '../../game/palette.js'
import { ROWS } from '../../game/gridMath.js'

const GAME_CONFIG = typeof __GAME_CONFIG__ !== 'undefined' ? __GAME_CONFIG__ : globalThis.__GAME_CONFIG__
const GRID_CONFIG = typeof __GRID_CONFIG__ !== 'undefined' ? __GRID_CONFIG__ : globalThis.__GRID_CONFIG__

function loadBest(storageKey) {
  if (typeof window === 'undefined') return 0
  const raw = window.localStorage.getItem(storageKey)
  const parsed = Number.parseInt(raw ?? '0', 10)
  return Number.isFinite(parsed) ? parsed : 0
}

function persistBest(storageKey, best) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(storageKey, String(best))
}

export default function SnakeGrid({ gridData }) {
  const weeks = gridData?.weeks ?? GRID_CONFIG?.weeks ?? 53
  const winScore = GAME_CONFIG?.win_score ?? 50
  const tickMs = GAME_CONFIG?.tick_ms ?? 120
  const storageKey = GAME_CONFIG?.best_storage_key ?? 'snake-tokscale:best'

  const [state, dispatch] = useReducer(
    gameReducer,
    undefined,
    () => createInitialState({ weeks, winScore, best: loadBest(storageKey) }),
  )

  useGameLoop(state.status, tickMs, dispatch)
  useKeyboard(dispatch)

  useEffect(() => {
    persistBest(storageKey, state.best)
  }, [state.best, storageKey])

  const cells = useMemo(() => gridData?.cells ?? fallbackCells(weeks), [gridData, weeks])
  const svgWidth = weeks * (CELL_SIZE + CELL_GAP) - CELL_GAP
  const svgHeight = ROWS * (CELL_SIZE + CELL_GAP) - CELL_GAP

  return (
    <section
      className="mx-auto flex w-full max-w-5xl flex-col gap-4 p-6"
      role="application"
      aria-label="Snake game"
      tabIndex={0}
    >
      <HUD
        score={state.score}
        best={state.best}
        target={winScore}
        username={gridData?.username}
        generatedAt={gridData?.generatedAt}
      />
      <div className="relative mx-auto overflow-hidden rounded-lg border border-neutral-800 bg-neutral-950 p-4">
        <svg
          width={svgWidth}
          height={svgHeight}
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="block"
        >
          <Grid cells={cells} weeks={weeks} />
          <Snake snake={state.snake} />
          <Food food={state.food} />
        </svg>
        <Overlays
          status={state.status}
          score={state.score}
          target={winScore}
          best={state.best}
        />
      </div>
    </section>
  )
}

function fallbackCells(weeks) {
  return Array.from({ length: weeks * ROWS }, (_, i) => ({
    date: '',
    tokens: 0,
    level: 0,
    key: i,
  }))
}
