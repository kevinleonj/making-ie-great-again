"""Upload reference audio to fal.ai CDN and clone voices via Qwen3-TTS.

Two-step process per leader:
  1. Upload the WAV file to fal CDN via fal_client.upload_file.
  2. Call fal-ai/qwen-3-tts/clone-voice/1.7b to generate a speaker
     embedding (safetensors) for use in TTS generation.

Reads transcripts from data/trump_transcript.txt and data/maduro_transcript.txt.
Saves output to data/fal_voice_config.json.

Usage:
    FAL_KEY=your-key python scripts/upload_ref_audio.py
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

import fal_client  # noqa: E402 — must import after dotenv loads FAL_KEY

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = DATA_DIR / "fal_voice_config.json"

CLONE_VOICE_MODEL = "fal-ai/qwen-3-tts/clone-voice/1.7b"

LEADERS: dict[str, dict[str, str]] = {
    "trump": {
        "audio_file": "trump_30s.wav",
        "transcript_file": "trump_transcript.txt",
    },
    "maduro": {
        "audio_file": "maduro_30s.wav",
        "transcript_file": "maduro_transcript.txt",
    },
}


def _read_transcript(transcript_path: Path) -> str:
    """Read and return transcript text from a file.

    Args:
        transcript_path: Path to the transcript text file.

    Returns:
        The transcript text, stripped of leading/trailing whitespace.

    Raises:
        FileNotFoundError: If the transcript file does not exist.
    """
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")
    return transcript_path.read_text(encoding="utf-8").strip()


def _upload_audio(audio_path: Path) -> str:
    """Upload an audio file to fal CDN.

    Args:
        audio_path: Path to the local WAV file.

    Returns:
        The fal CDN URL for the uploaded file.

    Raises:
        FileNotFoundError: If the audio file does not exist.
        RuntimeError: If the upload fails.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    logger.info("Uploading %s to fal CDN...", audio_path.name)
    try:
        url: str = fal_client.upload_file(audio_path)
    except Exception as exc:
        raise RuntimeError(f"Failed to upload {audio_path.name}: {exc}") from exc
    logger.info("Uploaded -> %s", url)
    return url


def _clone_voice(audio_url: str, reference_text: str) -> str:
    """Clone a voice by generating a speaker embedding via Qwen3-TTS.

    Args:
        audio_url: CDN URL of the reference audio.
        reference_text: Transcript of the reference audio.

    Returns:
        URL of the generated speaker embedding (.safetensors).

    Raises:
        RuntimeError: If the clone voice API call fails.
    """
    logger.info("Cloning voice via %s...", CLONE_VOICE_MODEL)
    try:
        result = fal_client.subscribe(
            CLONE_VOICE_MODEL,
            arguments={
                "audio_url": audio_url,
                "reference_text": reference_text,
            },
        )
    except Exception as exc:
        raise RuntimeError(f"Voice cloning failed: {exc}") from exc

    embedding_url: str = result["speaker_embedding"]["url"]
    logger.info("Got speaker embedding -> %s", embedding_url)
    return embedding_url


def process_leaders() -> dict[str, dict[str, str]]:
    """Upload audio and clone voice for each leader.

    Returns:
        Dictionary mapping leader name to voice config with audio_url,
        embedding_url, and reference_text.
    """
    voice_config: dict[str, dict[str, str]] = {}

    for leader, config in LEADERS.items():
        logger.info("Processing %s...", leader)

        audio_path = DATA_DIR / config["audio_file"]
        transcript_path = DATA_DIR / config["transcript_file"]

        reference_text = _read_transcript(transcript_path)
        audio_url = _upload_audio(audio_path)
        embedding_url = _clone_voice(audio_url, reference_text)

        voice_config[leader] = {
            "audio_url": audio_url,
            "embedding_url": embedding_url,
            "reference_text": reference_text,
        }
        logger.info("Done with %s", leader)

    return voice_config


def save_voice_config(voice_config: dict[str, dict[str, str]]) -> None:
    """Save voice configuration to a JSON file.

    Args:
        voice_config: Dictionary mapping leader name to voice config.
    """
    OUTPUT_FILE.write_text(json.dumps(voice_config, indent=2) + "\n", encoding="utf-8")
    logger.info("Saved voice config to %s", OUTPUT_FILE)


def main() -> None:
    """Upload reference audio, clone voices, and save configuration."""
    logger.info("Starting voice cloning pipeline")
    voice_config = process_leaders()
    save_voice_config(voice_config)
    logger.info("Done. Voice config:\n%s", json.dumps(voice_config, indent=2))


if __name__ == "__main__":
    main()
