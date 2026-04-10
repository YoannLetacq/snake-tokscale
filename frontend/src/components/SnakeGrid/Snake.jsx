import { CELL_SIZE, DEFAULT_PALETTE, cellX, cellY } from '../../game/palette.js'

// Snake overlay — draws each body cell as a slightly inset rounded rect so the
// heatmap colour stays visible underneath.
const TAPER_COUNT = 5
const TAIL_SHRINK = 5

function Snake({ snake, palette = DEFAULT_PALETTE }) {
  if (!snake?.length) return null
  const bodySize = CELL_SIZE - 2
  const bodyInset = 1
  const headSize = CELL_SIZE + 2
  const headOffset = -1

  return (
    <g>
      {snake.map((cell, idx) => {
        const isHead = idx === snake.length - 1
        // idx 0 = tail tip, idx length-1 = head
        const fromTail = idx
        let size, offset, rx
        if (isHead) {
          size = headSize; offset = headOffset; rx = 4
        } else if (fromTail < TAPER_COUNT) {
          const shrink = TAPER_COUNT - fromTail
          size = bodySize - shrink
          offset = bodyInset + shrink / 2
          rx = 2
        } else {
          size = bodySize; offset = bodyInset; rx = 3
        }
        return (
          <rect
            key={`snake-${cell.x}-${cell.y}-${idx}`}
            x={cellX(cell.x) + offset}
            y={cellY(cell.y) + offset}
            width={size}
            height={size}
            rx={rx}
            ry={rx}
            fill={isHead ? palette.head : palette.snake}
            opacity={isHead ? 1 : 0.92}
          />
        )
      })}
    </g>
  )
}

export default Snake
