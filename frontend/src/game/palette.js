// Tokscale-inspired palette: 5 levels from empty to hottest (purple).
export const LEVEL_COLORS = [
  '#161b22', // 0 — empty
  '#3d2b5b', // 1
  '#62448b', // 2
  '#8959bc', // 3
  '#b388eb', // 4
]

export const SNAKE_COLOR = '#e84749'
export const SNAKE_HEAD_COLOR = '#ff7b72'
export const FOOD_COLOR = '#ffffff'
export const FOOD_HALO = '#f1e05a'

export const CELL_SIZE = 12
export const CELL_GAP = 2

export function cellX(col) {
  return col * (CELL_SIZE + CELL_GAP)
}

export function cellY(row) {
  return row * (CELL_SIZE + CELL_GAP)
}
