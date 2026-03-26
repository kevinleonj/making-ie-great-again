"""TTS service using fal.ai F5-TTS for voice cloning."""

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
        "ref_transcript": "trump_transcript.txt",
        "lang_code": "english",
    },
    "maduro": {
        "ref_transcript": "maduro_transcript.txt",
        "lang_code": "spanish",
    },
}


class TTSService:
    """Text-to-speech service using fal.ai F5-TTS.

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
        self._transcripts: dict[str, str] = {}
        self._ref_audio_urls: dict[str, str] = {}

        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._load_transcripts()
        self._load_ref_audio_urls()
        self._configure_fal_key()

    def _configure_fal_key(self) -> None:
        """Set FAL_KEY in environment for fal_client authentication."""
        if self._fal_key and not self._mock:
            os.environ["FAL_KEY"] = self._fal_key

    def _load_transcripts(self) -> None:
        """Load reference transcripts from data directory."""
        for leader, config in _VOICE_CONFIG.items():
            transcript_path = self._data_dir / config["ref_transcript"]
            if transcript_path.exists():
                self._transcripts[leader] = transcript_path.read_text(encoding="utf-8").strip()
                logger.info(
                    "Loaded transcript for %s (%d chars)",
                    leader,
                    len(self._transcripts[leader]),
                )
            else:
                logger.warning("Transcript not found: %s", transcript_path)

    def _load_ref_audio_urls(self) -> None:
        """Load pre-uploaded fal CDN URLs for reference audio."""
        urls_file = self._data_dir / "fal_audio_urls.json"
        if urls_file.exists():
            data = json.loads(urls_file.read_text(encoding="utf-8"))
            self._ref_audio_urls = {k: str(v) for k, v in data.items()}
            logger.info("Loaded %d fal audio URLs", len(self._ref_audio_urls))
        else:
            if not self._mock:
                logger.warning(
                    "fal_audio_urls.json not found in %s. "
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
            ValueError: If leader is unknown or transcript missing.
            RuntimeError: If generation fails.
        """
        voice = _VOICE_CONFIG.get(leader)
        if voice is None:
            raise ValueError(f"Unknown leader: {leader}")

        transcript = self._transcripts.get(leader)
        if not transcript:
            raise ValueError(f"No transcript loaded for {leader}")

        filename = f"{leader}_{uuid.uuid4().hex[:8]}.wav"
        output_path = self._output_dir / filename

        if self._mock:
            return self._generate_mock(output_path, filename)

        return self._generate_real(leader, text, transcript, output_path, filename)

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
        transcript: str,
        output_path: Path,
        filename: str,
    ) -> TTSResult:
        """Generate real TTS audio using fal.ai F5-TTS API."""
        ref_audio_url = self._ref_audio_urls.get(leader)
        if not ref_audio_url:
            raise ValueError(
                f"No fal audio URL for {leader}. Run scripts/upload_ref_audio.py first."
            )

        logger.info("Generating TTS via fal.ai for %s: %s", leader, text[:80])
        start = time.time()

        try:
            result = fal_client.subscribe(
                self._fal_tts_model,
                arguments={
                    "gen_text": text,
                    "ref_audio_url": ref_audio_url,
                    "ref_text": transcript,
                    "model_type": "F5-TTS",
                    "remove_silence": True,
                },
            )
        except Exception as exc:
            raise RuntimeError(f"fal.ai TTS call failed: {exc}") from exc

        audio_url = result["audio_url"]["url"]
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
