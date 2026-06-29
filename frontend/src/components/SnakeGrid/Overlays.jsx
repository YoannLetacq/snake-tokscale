import { STATUS } from '../../game/gameReducer.js'

function Overlays({ status, score, target, best }) {
  if (status === STATUS.PLAYING) return null

  return (
    <div
      className="pointer-events-none absolute inset-0 flex items-center justify-center bg-neutral-950/70 backdrop-blur-sm"
      aria-live="polite"
    >
      <div className="pointer-events-auto text-center">
        {status === STATUS.IDLE && <IdleCard />}
        {status === STATUS.LOST && <LostCard score={score} best={best} />}
        {status === STATUS.WON && <WonCard target={target} />}
      </div>
    </div>
  )
}

function IdleCard() {
  return (
    <>
      <h1 className="text-5xl font-bold tracking-tight text-neutral-50">SNAKE</h1>
      <p className="mt-3 text-neutral-300">
        Appuyez sur <kbd className="rounded bg-neutral-800 px-2 py-0.5 text-xs">Espace</kbd> pour démarrer ·
        <kbd className="ml-1 rounded bg-neutral-800 px-2 py-0.5 text-xs">← ↑ → ↓</kbd> pour vous déplacer
      </p>
    </>
  )
}

function LostCard({ score, best }) {
  return (
    <>
      <h1 className="text-4xl font-bold text-red-400">Partie terminée</h1>
      <p className="mt-2 text-neutral-200">
        Score : <strong>{score}</strong> · Meilleur : <strong>{best}</strong>
      </p>
      <p className="mt-2 text-neutral-400 text-sm">
        Appuyez sur <kbd className="rounded bg-neutral-800 px-2 py-0.5 text-xs">Espace</kbd> pour réessayer
      </p>
    </>
  )
}

function WonCard({ target }) {
  return (
    <>
      <h1 className="text-4xl font-bold text-emerald-400 animate-pulse">Gagné !</h1>
      <p className="mt-2 text-neutral-200">Objectif de {target} atteint.</p>
      <p className="mt-2 text-neutral-400 text-sm">
        Appuyez sur <kbd className="rounded bg-neutral-800 px-2 py-0.5 text-xs">Espace</kbd> pour rejouer
      </p>
    </>
  )
}

export default Overlays
