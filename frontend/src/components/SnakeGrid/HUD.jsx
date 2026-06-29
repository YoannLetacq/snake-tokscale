function HUD({ score, best, target, username, generatedAt }) {
  return (
    <div className="flex flex-wrap items-baseline justify-between gap-4 text-sm text-neutral-300">
      <div className="flex gap-6">
        <span>
          Score <strong className="text-neutral-50">{score}</strong>
        </span>
        <span>
          Meilleur <strong className="text-neutral-50">{best}</strong>
        </span>
        <span>
          Objectif <strong className="text-neutral-50">{target}</strong>
        </span>
      </div>
      <div className="text-xs text-neutral-500">
        {username ? <>@{username} · </> : null}
        {generatedAt ? new Date(generatedAt).toLocaleString() : null}
      </div>
    </div>
  )
}

export default HUD
