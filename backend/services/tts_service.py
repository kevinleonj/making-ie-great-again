"""TTS service using fal.ai Qwen3-TTS for voice cloning."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

import fal_client
import httpx
import numpy as np
import soundfile as sf

from backend.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TTSResult:
    """Result of a TTS generation."""

    file_path: Path
    filename: str
    duration_seconds: float
    sample_rate: int


_VOICE_CONFIG: dict[str, dict[str, str]] = {
    "trump": {
        "language": "English",
    },
    "maduro": {
        "language": "Spanish",
    },
}


class TTSService:
    """Text-to-speech service using fal.ai Qwen3-TTS.

    Calls the fal.ai cloud API for voice cloning and saves the
    resulting audio locally. Supports a mock mode for testing
    without the cloud API.
    """

    def __init__(
        self,
        fal_key: str,
        fal_tts_model: str,
        data_dir: Path,
        output_dir: Path,
        mock: bool = False,
    ) -> None:
        self._fal_key = fal_key
        self._fal_tts_model = fal_tts_model
        self._data_dir = data_dir
        self._output_dir = output_dir
        self._mock = mock
        self._voice_configs: dict[str, dict[str, str]] = {}

        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._load_voice_config()
        self._configure_fal_key()

    def _configure_fal_key(self) -> None:
        """Set FAL_KEY in environment for fal_client authentication."""
        if self._fal_key and not self._mock:
            os.environ["FAL_KEY"] = self._fal_key

    def _load_voice_config(self) -> None:
        """Load pre-generated voice config with embeddings and reference text."""
        config_file = self._data_dir / "fal_voice_config.json"
        if config_file.exists():
            data = json.loads(config_file.read_text(encoding="utf-8"))
            for leader, config in data.items():
                self._voice_configs[leader] = {
                    "embedding_url": str(config["embedding_url"]),
                    "reference_text": str(config["reference_text"]),
                }
            logger.info("Loaded voice configs for %d leaders", len(self._voice_configs))
        else:
            if not self._mock:
                logger.warning(
                    "fal_voice_config.json not found in %s. "
                    "Run scripts/upload_ref_audio.py first.",
                    self._data_dir,
                )

    def resolve_audio_path(self, filename: str) -> Path:
        """Resolve an audio filename to its full path within the output directory.

        Args:
            filename: The audio file name.

        Returns:
            The absolute path to the audio file.

        Raises:
            ValueError: If the resolved path escapes the output directory.
        """
        file_path = self._output_dir / filename
        try:
            file_path.resolve().relative_to(self._output_dir.resolve())
        except ValueError as exc:
            raise ValueError(f"Invalid audio path: {filename}") from exc
        return file_path

    def generate(self, leader: str, text: str) -> TTSResult:
        """Generate speech audio for the given text in the leader's voice.

        Args:
            leader: "trump" or "maduro".
            text: Text to synthesize.

        Returns:
            TTSResult with file path and metadata.

        Raises:
            ValueError: If leader is unknown or voice config missing.
            RuntimeError: If generation fails.
        """
        voice = _VOICE_CONFIG.get(leader)
        if voice is None:
            raise ValueError(f"Unknown leader: {leader}")

        voice_config = self._voice_configs.get(leader)
        if not voice_config or not voice_config.get("reference_text"):
            raise ValueError(
                f"No voice config for {leader}. Run scripts/upload_ref_audio.py first."
            )

        filename = f"{leader}_{uuid.uuid4().hex[:8]}.wav"
        output_path = self._output_dir / filename

        if self._mock:
            return self._generate_mock(output_path, filename)

        return self._generate_real(leader, text, voice_config, output_path, filename)

    def _generate_mock(self, output_path: Path, filename: str) -> TTSResult:
        """Generate a mock silent WAV file for testing."""
        sample_rate = 24000
        duration = 3.0
        samples = np.zeros(int(sample_rate * duration), dtype=np.float32)
        sf.write(str(output_path), samples, sample_rate)
        logger.info("Mock audio generated: %s", filename)
        return TTSResult(
            file_path=output_path,
            filename=filename,
            duration_seconds=duration,
            sample_rate=sample_rate,
        )

    def _generate_real(
        self,
        leader: str,
        text: str,
        voice_config: dict[str, str],
        output_path: Path,
        filename: str,
    ) -> TTSResult:
        """Generate real TTS audio using fal.ai Qwen3-TTS API."""
        voice = _VOICE_CONFIG[leader]

        logger.info("Generating TTS via fal.ai Qwen3-TTS for %s: %s", leader, text[:80])
        start = time.time()

        try:
            result = fal_client.subscribe(
                self._fal_tts_model,
                arguments={
                    "text": text,
                    "language": voice["language"],
                    "speaker_voice_embedding_file_url": voice_config["embedding_url"],
                    "reference_text": voice_config["reference_text"],
                },
            )
        except Exception as exc:
            raise RuntimeError(f"fal.ai TTS call failed: {exc}") from exc

        audio_url = result["audio"]["url"]
        logger.info("fal.ai returned audio URL: %s", audio_url)

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.get(audio_url)
                response.raise_for_status()
                output_path.write_bytes(response.content)
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Failed to download generated audio: {exc}") from exc

        audio_data, sample_rate = sf.read(str(output_path))
        duration = len(audio_data) / sample_rate
        elapsed = time.time() - start

        logger.info(
            "TTS complete: %s (%.2fs audio, %.2fs processing)",
            filename,
            duration,
            elapsed,
        )

        return TTSResult(
            file_path=output_path,
            filename=filename,
            duration_seconds=duration,
            sample_rate=sample_rate,
        )


_tts_service: TTSService | None = None


def get_tts_service() -> TTSService:
    """Get or create the singleton TTS service.

    Returns:
        The shared TTSService instance.
    """
    global _tts_service  # noqa: PLW0603
    if _tts_service is None:
        settings = get_settings()
        project_root = Path(__file__).resolve().parent.parent.parent
        _tts_service = TTSService(
            fal_key=settings.fal_key,
            fal_tts_model=settings.fal_tts_model,
            data_dir=project_root / settings.data_dir,
            output_dir=project_root / settings.audio_output_dir,
            mock=settings.tts_mock,
        )
    return _tts_service
