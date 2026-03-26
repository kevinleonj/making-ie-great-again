"""Tests for the TTS service."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.services.tts_service import TTSService


def test_mock_generation(tmp_path: Path) -> None:
    """Mock mode generates a silent WAV file."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    output_dir = tmp_path / "output"

    # Create mock transcript files
    (data_dir / "trump_transcript.txt").write_text("Test transcript")
    (data_dir / "maduro_transcript.txt").write_text("Transcripcion de prueba")

    service = TTSService(
        fal_key="test-key",
        fal_tts_model="fal-ai/f5-tts",
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
    (data_dir / "trump_transcript.txt").write_text("Test")
    (data_dir / "maduro_transcript.txt").write_text("Prueba")

    service = TTSService(
        fal_key="test-key",
        fal_tts_model="fal-ai/f5-tts",
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
    (data_dir / "trump_transcript.txt").write_text("Test")
    (data_dir / "maduro_transcript.txt").write_text("Prueba")

    service = TTSService(
        fal_key="test-key",
        fal_tts_model="fal-ai/f5-tts",
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
    (data_dir / "trump_transcript.txt").write_text("Test")
    (data_dir / "maduro_transcript.txt").write_text("Prueba")

    output_dir = tmp_path / "output" / "nested"
    TTSService(
        fal_key="test-key",
        fal_tts_model="fal-ai/f5-tts",
        data_dir=data_dir,
        output_dir=output_dir,
        mock=True,
    )

    assert output_dir.exists()
