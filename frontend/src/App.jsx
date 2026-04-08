import { useEffect, useState } from 'react'
import SnakeGrid from './components/SnakeGrid/index.jsx'

const USERNAME = typeof __TOKSCALE_USERNAME__ !== 'undefined' ? __TOKSCALE_USERNAME__ : 'YoannLetacq'

export default function App() {
  const [gridData, setGridData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetch(`${import.meta.env.BASE_URL}grid.json`, { cache: 'no-cache' })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`grid.json HTTP ${response.status}`)
        }
        return response.json()
      })
      .then((data) => {
        if (!cancelled) setGridData(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <header className="border-b border-neutral-800 px-6 py-4">
        <h1 className="text-xl font-semibold">
          snake-tokscale <span className="text-neutral-500">/ @{USERNAME}</span>
        </h1>
        <p className="text-sm text-neutral-400">
          Play snake on your <a className="text-emerald-400 hover:underline" href="https://tokscale.ai">tokscale.ai</a> token-usage heatmap.
        </p>
      </header>
      {error ? (
        <p className="p-6 text-red-400">Failed to load grid.json: {error}</p>
      ) : (
        <SnakeGrid gridData={gridData} />
      )}
    </main>
  )
}
