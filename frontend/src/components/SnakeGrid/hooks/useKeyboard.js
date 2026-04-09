import { useEffect } from 'react'

const DIRECTION_KEYS = {
  ArrowUp: 'UP',
  ArrowDown: 'DOWN',
  ArrowLeft: 'LEFT',
  ArrowRight: 'RIGHT',
}

const GAMEPLAY_KEYS = new Set([...Object.keys(DIRECTION_KEYS), ' ', 'Space'])

// Global keyboard listener: Space starts/retries, arrows change direction.
// `onRestart` is fired on Space so the host can re-seed the reducer with
// the original grid cells — dispatching a bare {type:'START'} would let
// startGame fall back to the (already-eaten) state.cells and instant-win.
export function useKeyboard(dispatch, onRestart) {
  useEffect(() => {
    const handler = (event) => {
      if (GAMEPLAY_KEYS.has(event.key)) {
        event.preventDefault()
      }
      if (event.key === ' ' || event.key === 'Space') {
        onRestart()
        return
      }
      const direction = DIRECTION_KEYS[event.key]
      if (direction) {
        dispatch({ type: 'CHANGE_DIR', direction })
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [dispatch, onRestart])
}
