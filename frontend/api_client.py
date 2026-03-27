"""HTTP client for communicating with the backend API."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from frontend.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TransformResult:
    """Result of a text transformation API call."""

    original_text: str
    transformed_text: str
    leader: str
    language: str


@dataclass(frozen=True)
class TTSResult:
    """Result of a TTS generation API call."""

    audio_url: str
    duration_seconds: float
    sample_rate: int


class APIClient:
    """Client for the MakingIEGreatAgain backend API.

    Args:
        base_url: Base URL of the backend (e.g., "http://localhost:8000").
    """

    def __init__(self, base_url: str | None = None) -> None:
        if base_url is None:
            base_url = get_settings().backend_url
        self._base_url = base_url
        self._client = httpx.Client(base_url=base_url, timeout=180.0)

    def transform_text(self, leader: str, text: str) -> TransformResult:
        """Transform text into a leader's speaking style.

        Args:
            leader: "trump" or "maduro".
            text: Input text to transform.

        Returns:
            TransformResult with original and transformed text.

        Raises:
            httpx.HTTPStatusError: If the API returns an error.
            httpx.ConnectError: If the backend is unreachable.
        """
        logger.info("Calling /api/transform for %s", leader)
        response = self._client.post(
            "/api/transform",
            json={"leader": leader, "text": text},
        )
        response.raise_for_status()
        data = response.json()
        return TransformResult(
            original_text=data["original_text"],
            transformed_text=data["transformed_text"],
            leader=data["leader"],
            language=data["language"],
        )

    def generate_tts(self, leader: str, text: str) -> TTSResult:
        """Generate TTS audio for text in a leader's voice.

        Args:
            leader: "trump" or "maduro".
            text: Text to synthesize.

        Returns:
            TTSResult with audio URL and metadata.

        Raises:
            httpx.HTTPStatusError: If the API returns an error.
        """
        logger.info("Calling /api/tts for %s", leader)
        response = self._client.post(
            "/api/tts",
            json={"leader": leader, "text": text},
        )
        response.raise_for_status()
        data = response.json()
        return TTSResult(
            audio_url=data["audio_url"],
            duration_seconds=data["duration_seconds"],
            sample_rate=data["sample_rate"],
        )

    def get_audio_url(self, audio_path: str) -> str:
        """Build the full URL for an audio file.

        Args:
            audio_path: Relative audio path from API response
                (e.g., "/api/audio/file.wav").

        Returns:
            Full URL for the audio file.
        """
        return f"{self._base_url}{audio_path}"

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()


_api_client: APIClient | None = None


def get_api_client() -> APIClient:
    """Get or create the singleton API client.

    Returns:
        The shared APIClient instance.
    """
    global _api_client  # noqa: PLW0603
    if _api_client is None:
        _api_client = APIClient()
    return _api_client
