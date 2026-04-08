# snake-tokscale

A Snake that eats your **tokscale.ai** token-usage heatmap — inspired by
[`Platane/snk`](https://github.com/Platane/snk), but with two differences:

1. the grid comes from the public `https://tokscale.ai/api/users/<username>` endpoint
   (tokscale only ships raw data, so the CLI renders the heatmap itself), and
2. clicking the animated SVG opens a **playable** keyboard-controlled React version
   on GitHub Pages.

[![snake-tokscale animated grid](https://raw.githubusercontent.com/YoannLetacq/snake-tokscale/output/snake.svg)](https://yoannletacq.github.io/snake-tokscale/)

> Click the grid above to play the live version on GitHub Pages.

## Stack

- **Backend** — Python 3.12 + `uv`, CLI that fetches tokscale data and writes `grid.json`.
- **Frontend** — React 19 + Vite 7 + Tailwind 4, reducer-based Snake game.
- **CI/CD** — GitHub Actions (cron /6h + `workflow_dispatch` + push to `master`) deploying to GitHub Pages.

## Configuration

All non-secret configuration lives in [`config.toml`](./config.toml):

```toml
[tokscale]
username = "YoannLetacq"
api_base = "https://tokscale.ai/api"
timeout = 30

[grid]
weeks = 53
output = "frontend/public/grid.json"

[game]
tick_ms = 120
win_score = 50
```

Secrets (if ever needed) go in a local `.env` file — copy [`env.example`](./env.example) to `.env`:

```sh
cp env.example .env
```

The tokscale API is public, so no credentials are required today.

## Local development

### Backend

```sh
cd backend
uv sync
uv run pytest -v
uv run python -m snake_tokscale             # uses config.toml
```

### Frontend

```sh
cd frontend
npm ci
npm run dev    # http://localhost:5173/snake-tokscale/
npm test       # Vitest unit tests
```

## Controls

- **Space** — start / retry
- **← ↑ → ↓** — move the snake
- Eat the food markers to grow. Reach the target score to win.
- Your best score is persisted in `localStorage`.

## Deployment

Push to `master` (or trigger `refresh-and-deploy.yml` manually) — the workflow regenerates
`grid.json`, builds the Vite bundle, and publishes to GitHub Pages.

## Security

- No secrets committed.
- `.env` is git-ignored.
- Strict validation of the tokscale API response shape.
- Precise exceptions only (`ValueError`, `httpx.HTTPStatusError`).
