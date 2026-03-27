"""Backend configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


def _env(key: str, default: str) -> str:
    """Read a string environment variable with a default."""
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    """Read an integer environment variable with a default."""
    return int(os.environ.get(key, str(default)))


def _env_bool(key: str, default: bool) -> bool:
    """Read a boolean environment variable with a default."""
    val = os.environ.get(key, str(default)).lower()
    return val in ("true", "1", "yes")


@dataclass(frozen=True)
class BackendSettings:
    """Backend configuration from environment variables."""

    backend_host: str = field(default_factory=lambda: _env("BACKEND_HOST", "0.0.0.0"))
    backend_port: int = field(default_factory=lambda: _env_int("BACKEND_PORT", 8000))
    anthropic_api_key: str = field(default_factory=lambda: _env("ANTHROPIC_API_KEY", ""))
    anthropic_model: str = field(
        default_factory=lambda: _env("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    )
    fal_key: str = field(default_factory=lambda: _env("FAL_KEY", ""))
    fal_tts_model: str = field(
        default_factory=lambda: _env("FAL_TTS_MODEL", "fal-ai/qwen-3-tts/text-to-speech/1.7b")
    )
    tts_mock: bool = field(default_factory=lambda: _env_bool("TTS_MOCK", False))
    audio_output_dir: str = field(default_factory=lambda: _env("AUDIO_OUTPUT_DIR", "output"))
    data_dir: str = field(default_factory=lambda: _env("DATA_DIR", "data"))


_settings: BackendSettings | None = None


def get_settings() -> BackendSettings:
    """Return a cached settings instance."""
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = BackendSettings()
    return _settings
