"""Tests for configuration modules."""

from __future__ import annotations


def test_frontend_settings_defaults() -> None:
    """Frontend settings load with sensible defaults."""
    from frontend.config import get_settings

    settings = get_settings()
    assert settings.frontend_port == 8550
    assert settings.backend_url == "http://localhost:8000"
    assert settings.color_primary == "#000000"
    assert settings.color_accent_gold == "#C5A572"


def test_backend_settings_defaults() -> None:
    """Backend settings load with sensible defaults."""
    from backend.config import get_settings

    settings = get_settings()
    assert settings.backend_port == 8000
    assert settings.tts_mock is False
    assert settings.data_dir == "data"
