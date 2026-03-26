"""Upload reference audio files to fal.ai CDN storage.

One-time script that uploads local WAV files to fal's CDN and saves
the returned URLs to a JSON file for use by the TTS service.

Usage:
    FAL_KEY=your-key python scripts/upload_ref_audio.py
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import fal_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = DATA_DIR / "fal_audio_urls.json"

FILES_TO_UPLOAD: dict[str, str] = {
    "trump": "trump_30s.wav",
    "maduro": "maduro_30s.wav",
}


def upload_reference_audio() -> dict[str, str]:
    """Upload reference audio files and return a mapping of leader to CDN URL.

    Returns:
        Dictionary mapping leader name to fal CDN URL.

    Raises:
        FileNotFoundError: If a reference audio file does not exist.
        RuntimeError: If upload fails for any file.
    """
    urls: dict[str, str] = {}

    for leader, filename in FILES_TO_UPLOAD.items():
        file_path = DATA_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Reference audio not found: {file_path}")

        logger.info("Uploading %s (%s)...", leader, file_path.name)
        try:
            url: str = fal_client.upload_file(file_path)
        except Exception as exc:
            raise RuntimeError(f"Failed to upload {filename}: {exc}") from exc

        urls[leader] = url
        logger.info("Uploaded %s -> %s", leader, url)

    return urls


def save_urls(urls: dict[str, str]) -> None:
    """Save CDN URLs to a JSON file.

    Args:
        urls: Dictionary mapping leader name to CDN URL.
    """
    OUTPUT_FILE.write_text(json.dumps(urls, indent=2) + "\n", encoding="utf-8")
    logger.info("Saved URLs to %s", OUTPUT_FILE)


def main() -> None:
    """Upload reference audio files and save the resulting CDN URLs."""
    logger.info("Starting reference audio upload")
    urls = upload_reference_audio()
    save_urls(urls)
    logger.info("Done. URLs: %s", json.dumps(urls, indent=2))


if __name__ == "__main__":
    main()
