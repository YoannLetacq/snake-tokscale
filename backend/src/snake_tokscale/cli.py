"""Command-line entry point: fetch → normalize → write grid.json + snake.svg."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

from snake_tokscale.animate import render_animated_snake
from snake_tokscale.config import AppConfig, find_default_config, load_config
from snake_tokscale.fetch import fetch_user_contributions
from snake_tokscale.normalize import build_grid

logger = logging.getLogger("snake_tokscale")


def main(argv: list[str] | None = None) -> int:
    """Fetch contributions, normalize them, and persist grid.json + snake.svg."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = _parse_args(argv)

    try:
        config_path = Path(args.config) if args.config else find_default_config()
        config = load_config(config_path)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("config error: %s", exc)
        return 2

    repo_root = config_path.parent
    username = args.username or config.tokscale.username
    grid_output = Path(args.grid_out) if args.grid_out else _resolve(repo_root, config.grid.output)
    svg_output = Path(args.svg_out) if args.svg_out else _resolve(repo_root, config.svg.output)
    end = _parse_end_date(args.end_date)

    try:
        contributions = fetch_user_contributions(
            username,
            base_url=config.tokscale.api_base,
            timeout=config.tokscale.timeout,
        )
    except (httpx.HTTPError, ValueError) as exc:
        logger.error("fetch failed: %s", exc)
        return 1

    logger.info("fetched %d contributions for %s", len(contributions), username)
    cells = build_grid(contributions, end_date=end, weeks=config.grid.weeks)

    palette = _write_snake_svg(svg_output, cells, config)
    _write_grid_json(grid_output, cells, username, config, palette)

    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="snake_tokscale",
        description="Fetch tokscale contributions and generate grid.json + snake.svg.",
    )
    parser.add_argument("--config", help="Path to config.toml (default: walk up from cwd).")
    parser.add_argument("--username", help="Override [tokscale].username.")
    parser.add_argument("--grid-out", help="Override [grid].output.")
    parser.add_argument("--svg-out", help="Override [svg].output.")
    parser.add_argument(
        "--end-date",
        help="ISO end date for the grid window (default: today, UTC).",
    )
    return parser.parse_args(argv)


def _parse_end_date(raw: str | None) -> date:
    if raw is None:
        return datetime.now(timezone.utc).date()
    return date.fromisoformat(raw)


def _resolve(repo_root: Path, output: str) -> Path:
    path = Path(output)
    return path if path.is_absolute() else repo_root / path


def _write_grid_json(path: Path, cells, username: str, config: AppConfig, palette) -> None:
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "username": username,
        "weeks": config.grid.weeks,
        "palette": {
            "name": palette.name,
            "levels": list(palette.levels),
            "snake": palette.snake,
            "head": palette.head,
        },
        "cells": cells,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    logger.info("wrote %d cells to %s", len(cells), path)


def _write_snake_svg(path: Path, cells, config: AppConfig):
    svg, palette = render_animated_snake(
        cells,
        weeks=config.grid.weeks,
        snake_length=config.svg.snake_length,
        _duration_s=config.svg.duration_s,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    logger.info("wrote animated SVG to %s (%d bytes)", path, len(svg))
    return palette
