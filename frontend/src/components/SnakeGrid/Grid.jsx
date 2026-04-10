import { memo } from 'react'
import { CELL_SIZE, DEFAULT_PALETTE, cellX, cellY } from '../../game/palette.js'
import { ROWS } from '../../game/gridMath.js'

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

// Heatmap `<g>` layer — column-major, row 0 = Sunday at the top.
function Grid({ cells, weeks, palette = DEFAULT_PALETTE }) {
  const levelColors = palette.levels
  // Extract unique months and their column positions
  const monthLabels = []
  let lastMonth = -1
  for (let col = 0; col < weeks; col += 1) {
    const cell = cells[col * ROWS]
    if (cell?.date) {
      const month = new Date(cell.date).getMonth()
      if (month !== lastMonth) {
        monthLabels.push({ month: MONTHS[month], col })
        lastMonth = month
      }
    }
  }

  return (
    <g aria-label="tokscale heatmap">
      {/* Month labels at the top */}
      <g className="text-[9px] fill-neutral-500">
        {monthLabels.map(({ month, col }) => (
          <text key={`${month}-${col}`} x={cellX(col)} y={-8}>
            {month}
          </text>
        ))}
      </g>

      {/* Day labels on the left (only Mon, Wed, Fri as per GH style) */}
      <g className="text-[9px] fill-neutral-500" transform="translate(-25, 0)">
        <text y={cellY(1) + 9}>Mon</text>
        <text y={cellY(3) + 9}>Wed</text>
        <text y={cellY(5) + 9}>Fri</text>
      </g>

      {/* Grid cells */}
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
            fill={levelColors[cell.level] ?? levelColors[0]}
          />
        )
      })}
    </g>
  )
}

export default memo(Grid)
