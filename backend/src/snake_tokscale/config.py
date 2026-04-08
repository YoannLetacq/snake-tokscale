"""Load configuration from the repo-root ``config.toml``."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TokscaleConfig:
    """Settings for the tokscale.ai HTTP client."""

    username: str
    api_base: str
    timeout: float


@dataclass(frozen=True)
class GridConfig:
    """Settings for the generated grid.json file."""

    weeks: int
    output: str


@dataclass(frozen=True)
class SvgConfig:
    """Settings for the animated snake SVG."""

    output: str
    snake_length: int
    duration_s: float


@dataclass(frozen=True)
class AppConfig:
    """Top-level configuration bundle loaded from config.toml."""

    tokscale: TokscaleConfig
    grid: GridConfig
    svg: SvgConfig


def load_config(path: Path | str) -> AppConfig:
    """Parse ``config.toml`` at ``path`` and return a typed ``AppConfig``."""
    config_path = Path(path)
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)

    tokscale_raw = raw.get("tokscale", {})
    grid_raw = raw.get("grid", {})
    svg_raw = raw.get("svg", {})

    username = tokscale_raw.get("username")
    if not isinstance(username, str) or not username:
        raise ValueError("config.toml: [tokscale].username must be a non-empty string")

    return AppConfig(
        tokscale=TokscaleConfig(
            username=username,
            api_base=str(tokscale_raw.get("api_base", "https://tokscale.ai")),
            timeout=float(tokscale_raw.get("timeout", 30)),
        ),
        grid=GridConfig(
            weeks=int(grid_raw.get("weeks", 53)),
            output=str(grid_raw.get("output", "frontend/public/grid.json")),
        ),
        svg=SvgConfig(
            output=str(svg_raw.get("output", "dist/snake.svg")),
            snake_length=int(svg_raw.get("snake_length", 4)),
            duration_s=float(svg_raw.get("duration_s", 30.0)),
        ),
    )


def find_default_config(start: Path | None = None) -> Path:
    """Walk upwards from ``start`` until a ``config.toml`` is found."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        config = candidate / "config.toml"
        if config.is_file():
            return config
    raise FileNotFoundError("config.toml not found in current directory or any parent")
