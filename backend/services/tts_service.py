"""TTS service wrapping mlx-audio for voice cloning."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

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
        "ref_audio": "trump_30s.wav",
        "ref_transcript": "trump_transcript.txt",
        "lang_code": "english",
    },
    "maduro": {
        "ref_audio": "maduro_30s.wav",
        "ref_transcript": "maduro_transcript.txt",
        "lang_code": "spanish",
    },
}


class TTSService:
    """Text-to-speech service using mlx-audio Qwen3-TTS.

    Loads the model once and generates audio for each request.
    Supports a mock mode for testing without the ML model.
    """

    def __init__(self, model_id: str, data_dir: Path, output_dir: Path, mock: bool = False) -> None:
        self._model_id = model_id
        self._data_dir = data_dir
        self._output_dir = output_dir
        self._mock = mock
        self._model: object | None = None  # Lazy loaded
        self._transcripts: dict[str, str] = {}

        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._load_transcripts()

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

    def _ensure_model(self) -> None:
        """Load the TTS model if not already loaded.

        The mlx-audio import is deferred to this method intentionally.
        The ML framework is heavy and should only be imported when a real
        (non-mock) generation is actually requested, keeping startup fast.
        """
        if self._model is not None or self._mock:
            return

        logger.info("Loading TTS model: %s", self._model_id)
        start = time.time()
        # Deferred import: mlx-audio is a heavy ML framework that should only
        # load when actually needed, not at module import time.
        from mlx_audio.tts.utils import load_model

        self._model = load_model(self._model_id)
        elapsed = time.time() - start
        logger.info("TTS model loaded in %.1fs", elapsed)

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

        return self._generate_real(leader, text, voice, transcript, output_path, filename)

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
        voice: dict[str, str],
        transcript: str,
        output_path: Path,
        filename: str,
    ) -> TTSResult:
        """Generate real TTS audio using mlx-audio."""
        self._ensure_model()

        ref_audio_path = self._data_dir / voice["ref_audio"]
        if not ref_audio_path.exists():
            raise FileNotFoundError(f"Reference audio not found: {ref_audio_path}")

        logger.info("Generating TTS for %s: %s", leader, text[:80])
        start = time.time()

        results = list(
            self._model.generate(  # type: ignore[union-attr]
                text=text,
                ref_audio=str(ref_audio_path),
                ref_text=transcript,
                lang_code=voice["lang_code"],
                verbose=False,
            )
        )

        if not results:
            raise RuntimeError("No audio returned from TTS model")

        result = results[0]
        audio_np = np.array(result.audio)
        if audio_np.ndim > 1:
            audio_np = audio_np.squeeze()

        sample_rate = result.sample_rate
        sf.write(str(output_path), audio_np, sample_rate)

        duration = len(audio_np) / sample_rate
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
        project_root = Path(__file__).resolve().parent.parent
        _tts_service = TTSService(
            model_id=settings.tts_model_id,
            data_dir=project_root / settings.data_dir,
            output_dir=project_root / settings.audio_output_dir,
            mock=settings.tts_mock,
        )
    return _tts_service
