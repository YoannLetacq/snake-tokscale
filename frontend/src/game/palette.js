// Default palette (purple) — overridden at runtime by grid.json palette.
export const DEFAULT_PALETTE = {
  levels: ['#161b22', '#3d2b5b', '#62448b', '#8959bc', '#b388eb'],
  snake: '#e84749',
  head: '#ff7b72',
}

export const FOOD_COLOR = '#ffffff'
export const FOOD_HALO = '#f1e05a'

export const CELL_SIZE = 15
export const CELL_GAP = 2

export function cellX(col) {
  return col * (CELL_SIZE + CELL_GAP)
}

export function cellY(row) {
  return row * (CELL_SIZE + CELL_GAP)
}
