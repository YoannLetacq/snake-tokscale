"""Command-line entry point: fetch → normalize → write grid.json."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

from snake_tokscale.config import AppConfig, find_default_config, load_config
from snake_tokscale.fetch import fetch_user_contributions
from snake_tokscale.normalize import build_grid

logger = logging.getLogger("snake_tokscale")


def main(argv: list[str] | None = None) -> int:
    """Fetch contributions, normalize them, and persist ``grid.json``."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = _parse_args(argv)

    try:
        config = load_config(args.config) if args.config else load_config(find_default_config())
    except (FileNotFoundError, ValueError) as exc:
        logger.error("config error: %s", exc)
        return 2

    username = args.username or config.tokscale.username
    output_path = Path(args.out) if args.out else _resolve_output(config)
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
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "username": username,
        "weeks": config.grid.weeks,
        "cells": cells,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    logger.info("wrote %d cells to %s", len(cells), output_path)
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="snake_tokscale",
        description="Fetch tokscale contributions and generate grid.json.",
    )
    parser.add_argument("--config", help="Path to config.toml (default: walk up from cwd).")
    parser.add_argument("--username", help="Override [tokscale].username from config.toml.")
    parser.add_argument("--out", help="Override [grid].output from config.toml.")
    parser.add_argument(
        "--end-date",
        help="ISO end date for the grid window (default: today, UTC).",
    )
    return parser.parse_args(argv)


def _parse_end_date(raw: str | None) -> date:
    if raw is None:
        return datetime.now(timezone.utc).date()
    return date.fromisoformat(raw)


def _resolve_output(config: AppConfig) -> Path:
    output = Path(config.grid.output)
    if output.is_absolute():
        return output
    repo_root = find_default_config().parent
    return repo_root / output
