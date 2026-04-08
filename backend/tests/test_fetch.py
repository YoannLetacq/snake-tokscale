"""Tests for the fetch module (httpx client → tokscale response dict)."""

from __future__ import annotations

import httpx
import pytest

from snake_tokscale.fetch import fetch_user_contributions


def _mock_transport(handler):
    return httpx.MockTransport(handler)


class TestFetchUserContributions:
    def test_returns_contributions_list(self, tokscale_sample):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path.endswith("/api/users/testuser")
            return httpx.Response(200, json=tokscale_sample)

        client = httpx.Client(transport=_mock_transport(handler), base_url="https://tokscale.ai")
        payload = fetch_user_contributions("testuser", client=client)
        assert isinstance(payload, list)
        assert payload[0]["date"] == "2026-04-08"

    def test_raises_on_http_error(self):
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, json={"error": "not found"})

        client = httpx.Client(transport=_mock_transport(handler), base_url="https://tokscale.ai")
        with pytest.raises(httpx.HTTPStatusError):
            fetch_user_contributions("ghost", client=client)

    def test_raises_when_contributions_missing(self):
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"user": {}, "stats": {}})

        client = httpx.Client(transport=_mock_transport(handler), base_url="https://tokscale.ai")
        with pytest.raises(ValueError, match="contributions"):
            fetch_user_contributions("noshape", client=client)

    def test_raises_when_contributions_wrong_type(self):
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"contributions": "nope"})

        client = httpx.Client(transport=_mock_transport(handler), base_url="https://tokscale.ai")
        with pytest.raises(ValueError):
            fetch_user_contributions("x", client=client)
