"""Tests for the TTS service."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.services.tts_service import TTSService

FAL_TTS_MODEL = "fal-ai/qwen-3-tts/text-to-speech/1.7b"


def _create_test_data(data_dir: Path) -> None:
    """Create mock transcript files and voice config for tests."""
    (data_dir / "trump_transcript.txt").write_text("Test transcript")
    (data_dir / "maduro_transcript.txt").write_text("Transcripcion de prueba")

    voice_config = {
        "trump": {
            "audio_url": "https://fal.media/test/trump.wav",
            "embedding_url": "https://fal.media/test/trump.safetensors",
            "reference_text": "Test transcript",
        },
        "maduro": {
            "audio_url": "https://fal.media/test/maduro.wav",
            "embedding_url": "https://fal.media/test/maduro.safetensors",
            "reference_text": "Transcripcion de prueba",
        },
    }
    (data_dir / "fal_voice_config.json").write_text(
        json.dumps(voice_config, indent=2), encoding="utf-8"
    )


def test_mock_generation(tmp_path: Path) -> None:
    """Mock mode generates a silent WAV file."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    output_dir = tmp_path / "output"

    _create_test_data(data_dir)

    service = TTSService(
        fal_key="test-key",
        fal_tts_model=FAL_TTS_MODEL,
        data_dir=data_dir,
        output_dir=output_dir,
        mock=True,
    )

    result = service.generate("trump", "This is a test")
    assert result.file_path.exists()
    assert result.duration_seconds == 3.0
    assert result.sample_rate == 24000
    assert result.filename.startswith("trump_")
    assert result.filename.endswith(".wav")


def test_mock_generation_maduro(tmp_path: Path) -> None:
    """Mock mode works for Maduro too."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _create_test_data(data_dir)

    service = TTSService(
        fal_key="test-key",
        fal_tts_model=FAL_TTS_MODEL,
        data_dir=data_dir,
        output_dir=tmp_path / "output",
        mock=True,
    )

    result = service.generate("maduro", "Hola mundo")
    assert result.file_path.exists()
    assert result.filename.startswith("maduro_")


def test_unknown_leader_raises(tmp_path: Path) -> None:
    """Unknown leader raises ValueError."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _create_test_data(data_dir)

    service = TTSService(
        fal_key="test-key",
        fal_tts_model=FAL_TTS_MODEL,
        data_dir=data_dir,
        output_dir=tmp_path / "output",
        mock=True,
    )

    with pytest.raises(ValueError, match="Unknown leader"):
        service.generate("obama", "Hello")


def test_output_dir_created(tmp_path: Path) -> None:
    """Output directory is created automatically."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    _create_test_data(data_dir)

    output_dir = tmp_path / "output" / "nested"
    TTSService(
        fal_key="test-key",
        fal_tts_model=FAL_TTS_MODEL,
        data_dir=data_dir,
        output_dir=output_dir,
        mock=True,
    )

    assert output_dir.exists()
