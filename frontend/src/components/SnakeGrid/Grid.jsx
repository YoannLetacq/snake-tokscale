import { memo } from 'react'
import { CELL_SIZE, LEVEL_COLORS, cellX, cellY } from '../../game/palette.js'
import { ROWS } from '../../game/gridMath.js'

// Heatmap `<g>` layer — column-major, row 0 = Sunday at the top.
function Grid({ cells }) {
  return (
    <g aria-label="tokscale heatmap">
      {cells.map((cell, idx) => {
        const col = Math.floor(idx / ROWS)
        const row = idx % ROWS
        return (
          <rect
            key={`${col}-${row}`}
            x={cellX(col)}
            y={cellY(row)}
            width={CELL_SIZE}
            height={CELL_SIZE}
            rx={2}
            ry={2}
            fill={LEVEL_COLORS[cell.level] ?? LEVEL_COLORS[0]}
          />
        )
      })}
    </g>
  )
}

export default memo(Grid)
