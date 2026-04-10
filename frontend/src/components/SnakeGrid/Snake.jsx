import { CELL_SIZE, SNAKE_COLOR, SNAKE_HEAD_COLOR, cellX, cellY } from '../../game/palette.js'

// Snake overlay — draws each body cell as a slightly inset rounded rect so the
// heatmap colour stays visible underneath.
function Snake({ snake }) {
  if (!snake?.length) return null
  const bodyInset = 1.5
  const bodySize = CELL_SIZE - bodyInset * 2
  const headSize = CELL_SIZE + 2
  const headOffset = -1 // extend 1px beyond the cell on each side

  return (
    <g>
      {snake.map((cell, idx) => {
        const isHead = idx === snake.length - 1
        const size = isHead ? headSize : bodySize
        const offset = isHead ? headOffset : bodyInset
        return (
          <rect
            key={`snake-${cell.x}-${cell.y}-${idx}`}
            x={cellX(cell.x) + offset}
            y={cellY(cell.y) + offset}
            width={size}
            height={size}
            rx={isHead ? 4 : 3}
            ry={isHead ? 4 : 3}
            fill={isHead ? SNAKE_HEAD_COLOR : SNAKE_COLOR}
            opacity={isHead ? 1 : 0.92}
          />
        )
      })}
    </g>
  )
}

export default Snake
