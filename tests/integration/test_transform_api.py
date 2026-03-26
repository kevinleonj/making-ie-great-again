"""Integration tests for the transform API endpoint."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.integration
class TestTransformAPI:
    """Transform endpoint integration tests."""

    def test_transform_health_check(self, backend_url: str, backend_available: bool) -> None:
        """Backend health check returns 200."""
        if not backend_available:
            pytest.skip("Backend not available")
        resp = httpx.get(f"{backend_url}/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_transform_trump(self, backend_url: str, backend_available: bool) -> None:
        """Transform endpoint returns transformed text for Trump."""
        if not backend_available:
            pytest.skip("Backend not available")
        resp = httpx.post(
            f"{backend_url}/api/transform",
            json={"leader": "trump", "text": "We need better schools"},
            timeout=30.0,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["leader"] == "trump"
        assert data["language"] == "en"
        assert data["original_text"] == "We need better schools"
        assert len(data["transformed_text"]) > 0

    def test_transform_maduro(self, backend_url: str, backend_available: bool) -> None:
        """Transform endpoint returns Spanish text for Maduro."""
        if not backend_available:
            pytest.skip("Backend not available")
        resp = httpx.post(
            f"{backend_url}/api/transform",
            json={"leader": "maduro", "text": "We need unity"},
            timeout=30.0,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["leader"] == "maduro"
        assert data["language"] == "es"
        assert len(data["transformed_text"]) > 0

    def test_transform_invalid_leader(self, backend_url: str, backend_available: bool) -> None:
        """Transform endpoint returns 422 for invalid leader."""
        if not backend_available:
            pytest.skip("Backend not available")
        resp = httpx.post(
            f"{backend_url}/api/transform",
            json={"leader": "obama", "text": "Hello"},
        )
        assert resp.status_code == 422

    def test_transform_empty_text(self, backend_url: str, backend_available: bool) -> None:
        """Transform endpoint returns 422 for empty text."""
        if not backend_available:
            pytest.skip("Backend not available")
        resp = httpx.post(
            f"{backend_url}/api/transform",
            json={"leader": "trump", "text": ""},
        )
        assert resp.status_code == 422

    def test_transform_text_too_long(self, backend_url: str, backend_available: bool) -> None:
        """Transform endpoint returns 422 for text over 500 chars."""
        if not backend_available:
            pytest.skip("Backend not available")
        resp = httpx.post(
            f"{backend_url}/api/transform",
            json={"leader": "trump", "text": "x" * 501},
        )
        assert resp.status_code == 422
