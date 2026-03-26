"""Integration tests for the TTS API endpoint."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.integration
class TestTTSAPI:
    """TTS endpoint integration tests."""

    def test_tts_trump(self, backend_url: str, backend_available: bool) -> None:
        """TTS endpoint generates audio for Trump."""
        if not backend_available:
            pytest.skip("Backend not available")
        resp = httpx.post(
            f"{backend_url}/api/tts",
            json={"leader": "trump", "text": "This is tremendous"},
            timeout=120.0,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["audio_url"].startswith("/api/audio/")
        assert data["duration_seconds"] > 0
        assert data["sample_rate"] == 24000

    def test_tts_audio_served(self, backend_url: str, backend_available: bool) -> None:
        """Generated audio file can be fetched."""
        if not backend_available:
            pytest.skip("Backend not available")
        # First generate
        resp = httpx.post(
            f"{backend_url}/api/tts",
            json={"leader": "trump", "text": "Test"},
            timeout=120.0,
        )
        if resp.status_code != 200:
            pytest.skip("TTS generation failed (model may not be loaded)")

        audio_url = resp.json()["audio_url"]
        # Then fetch
        audio_resp = httpx.get(f"{backend_url}{audio_url}")
        assert audio_resp.status_code == 200
        assert audio_resp.headers.get("content-type", "").startswith("audio/")
        assert len(audio_resp.content) > 0

    def test_tts_invalid_leader(self, backend_url: str, backend_available: bool) -> None:
        """TTS endpoint returns 422 for invalid leader."""
        if not backend_available:
            pytest.skip("Backend not available")
        resp = httpx.post(
            f"{backend_url}/api/tts",
            json={"leader": "obama", "text": "Hello"},
        )
        assert resp.status_code == 422

    def test_audio_not_found(self, backend_url: str, backend_available: bool) -> None:
        """Fetching non existent audio returns 404."""
        if not backend_available:
            pytest.skip("Backend not available")
        resp = httpx.get(f"{backend_url}/api/audio/nonexistent.wav")
        assert resp.status_code == 404
