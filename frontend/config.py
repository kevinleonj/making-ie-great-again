"""Frontend configuration loaded from environment variables."""

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


@dataclass(frozen=True)
class FrontendSettings:
    """Frontend configuration from environment variables."""

    frontend_port: int = field(default_factory=lambda: _env_int("FRONTEND_PORT", 8550))
    backend_url: str = field(default_factory=lambda: _env("BACKEND_URL", "http://localhost:8000"))
    color_primary: str = field(default_factory=lambda: _env("COLOR_PRIMARY", "#000000"))
    color_accent_gold: str = field(default_factory=lambda: _env("COLOR_ACCENT_GOLD", "#C5A572"))
    color_surface: str = field(default_factory=lambda: _env("COLOR_SURFACE", "#FFFFFF"))
    color_on_surface: str = field(default_factory=lambda: _env("COLOR_ON_SURFACE", "#1A1A1A"))
    max_input_length: int = field(default_factory=lambda: _env_int("MAX_INPUT_LENGTH", 500))


_settings: FrontendSettings | None = None


def get_settings() -> FrontendSettings:
    """Return a cached settings instance."""
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = FrontendSettings()
    return _settings
