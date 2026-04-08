import '@testing-library/jest-dom/vitest'

// Inject config constants normally provided by Vite's define plugin.
globalThis.__GAME_CONFIG__ = globalThis.__GAME_CONFIG__ ?? {
  tick_ms: 120,
  win_score: 50,
  best_storage_key: 'snake-tokscale:best',
}
globalThis.__GRID_CONFIG__ = globalThis.__GRID_CONFIG__ ?? {
  weeks: 53,
  output: 'frontend/public/grid.json',
}
globalThis.__TOKSCALE_USERNAME__ = globalThis.__TOKSCALE_USERNAME__ ?? 'YoannLetacq'
