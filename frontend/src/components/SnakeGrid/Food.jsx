import { CELL_SIZE, FOOD_COLOR, FOOD_HALO, cellX, cellY } from '../../game/palette.js'

// Food marker — white dot with a pulsing halo for visibility against any heatmap cell.
function Food({ food }) {
  if (!food) return null
  const cx = cellX(food.x) + CELL_SIZE / 2
  const cy = cellY(food.y) + CELL_SIZE / 2

  return (
    <g>
      <circle cx={cx} cy={cy} r={CELL_SIZE / 2 + 1} fill={FOOD_HALO} opacity={0.35}>
        <animate
          attributeName="r"
          values={`${CELL_SIZE / 2 + 1};${CELL_SIZE / 2 + 3};${CELL_SIZE / 2 + 1}`}
          dur="1.2s"
          repeatCount="indefinite"
        />
      </circle>
      <circle cx={cx} cy={cy} r={CELL_SIZE / 3} fill={FOOD_COLOR} />
    </g>
  )
}

export default Food
