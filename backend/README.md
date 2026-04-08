# snake-tokscale — backend

Python 3.12 CLI that fetches token-usage contributions from the public
`tokscale.ai` API and emits the `grid.json` consumed by the frontend.

## Setup

```sh
uv sync
```

## Test

```sh
uv run pytest -v
```

## Run

```sh
# uses ../config.toml automatically
uv run python -m snake_tokscale

# overrides
uv run python -m snake_tokscale --username YoannLetacq --out /tmp/grid.json --end-date 2026-04-08
```

## Modules

| Module | Role |
|---|---|
| `fetch.py` | `httpx` GET `/api/users/<username>`, validates the payload shape. |
| `normalize.py` | Contributions → 53×7 `Sunday..Saturday` grid, missing days padded with 0. |
| `quantiles.py` | Non-zero tokens → quartile buckets (levels 1-4), zeros → level 0. |
| `config.py` | Loads `config.toml` (TOML via `tomllib`), walks upward to find it. |
| `cli.py` | Orchestrates fetch → normalize → write JSON. |
