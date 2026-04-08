import { CELL_SIZE, SNAKE_COLOR, SNAKE_HEAD_COLOR, cellX, cellY } from '../../game/palette.js'

// Snake overlay — draws each body cell as a slightly inset rounded rect so the
// heatmap colour stays visible underneath.
function Snake({ snake }) {
  if (!snake?.length) return null
  const inset = 1.5
  const size = CELL_SIZE - inset * 2

  return (
    <g>
      {snake.map((cell, idx) => {
        const isHead = idx === snake.length - 1
        return (
          <rect
            key={`snake-${cell.x}-${cell.y}-${idx}`}
            x={cellX(cell.x) + inset}
            y={cellY(cell.y) + inset}
            width={size}
            height={size}
            rx={3}
            ry={3}
            fill={isHead ? SNAKE_HEAD_COLOR : SNAKE_COLOR}
            opacity={isHead ? 1 : 0.92}
          />
        )
      })}
    </g>
  )
}

export default Snake
