import { useEffect } from 'react'
import { STATUS } from '../../../game/gameReducer.js'

// Fires a TICK action at a steady interval while the game is PLAYING.
// Pauses automatically when the browser tab loses visibility.
export function useGameLoop(status, tickMs, dispatch) {
  useEffect(() => {
    if (status !== STATUS.PLAYING) return undefined
    if (typeof document !== 'undefined' && document.hidden) return undefined

    const id = setInterval(() => dispatch({ type: 'TICK' }), tickMs)
    const onVisibility = () => {
      if (document.hidden) {
        clearInterval(id)
      }
    }
    document.addEventListener('visibilitychange', onVisibility)
    return () => {
      clearInterval(id)
      document.removeEventListener('visibilitychange', onVisibility)
    }
  }, [status, tickMs, dispatch])
}
