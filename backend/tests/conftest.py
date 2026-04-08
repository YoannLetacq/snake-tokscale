"""Shared pytest fixtures for snake_tokscale backend tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def tokscale_sample() -> dict[str, Any]:
    """Load the anonymised tokscale API response used across tests."""
    with (FIXTURES_DIR / "tokscale_sample.json").open(encoding="utf-8") as handle:
        return json.load(handle)
