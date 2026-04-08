import { useEffect } from 'react'

const DIRECTION_KEYS = {
  ArrowUp: 'UP',
  ArrowDown: 'DOWN',
  ArrowLeft: 'LEFT',
  ArrowRight: 'RIGHT',
}

const GAMEPLAY_KEYS = new Set([...Object.keys(DIRECTION_KEYS), ' ', 'Space'])

// Global keyboard listener: Space starts/retries, arrows change direction.
export function useKeyboard(dispatch) {
  useEffect(() => {
    const handler = (event) => {
      if (GAMEPLAY_KEYS.has(event.key)) {
        event.preventDefault()
      }
      if (event.key === ' ' || event.key === 'Space') {
        dispatch({ type: 'START' })
        return
      }
      const direction = DIRECTION_KEYS[event.key]
      if (direction) {
        dispatch({ type: 'CHANGE_DIR', direction })
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [dispatch])
}
