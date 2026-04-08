"""HTTP client for the public tokscale.ai user endpoint."""

from __future__ import annotations

from typing import Any

import httpx

DEFAULT_BASE_URL = "https://tokscale.ai"
DEFAULT_TIMEOUT = 30.0


def fetch_user_contributions(
    username: str,
    *,
    client: httpx.Client | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
) -> list[dict[str, Any]]:
    """Return the raw ``contributions`` list for ``username``.

    Accepts an optional pre-built :class:`httpx.Client` (useful in tests for
    mocking). Raises :class:`httpx.HTTPStatusError` on non-2xx responses and
    :class:`ValueError` when the JSON payload is missing the ``contributions``
    field or has an unexpected shape.
    """
    owns_client = client is None
    http = client or httpx.Client(base_url=base_url, timeout=timeout)
    try:
        response = http.get(f"/api/users/{username}")
        response.raise_for_status()
        payload = response.json()
    finally:
        if owns_client:
            http.close()

    return _extract_contributions(payload)


def _extract_contributions(payload: Any) -> list[dict[str, Any]]:
    """Validate the payload shape and return the contributions list."""
    if not isinstance(payload, dict):
        raise ValueError("tokscale response is not a JSON object")
    if "contributions" not in payload:
        raise ValueError("tokscale response is missing 'contributions'")
    contributions = payload["contributions"]
    if not isinstance(contributions, list):
        raise ValueError("tokscale response 'contributions' must be a list")
    return contributions
