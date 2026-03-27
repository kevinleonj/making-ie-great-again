"""Audio player component with browser-native playback and download."""

from __future__ import annotations

import logging

import flet as ft
from flet.controls.services.url_launcher import UrlLauncher

from frontend.theme import (
    ACCENT_GOLD,
    DIVIDER,
    ON_SURFACE,
    PRIMARY,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SURFACE_DIM,
)

logger = logging.getLogger(__name__)

_MAX_WIDTH = 600
_BORDER_RADIUS = 12


def build_audio_player(
    audio_url: str,
    page: ft.Page,
) -> ft.Container:
    """Build an audio player with browser-native playback.

    Opens the audio URL in a new browser tab for native HTML5 playback,
    since flet_audio's Audio widget is not registered in the Flet web
    runtime and throws "Unknown control: Audio".

    Args:
        audio_url: Full URL to the audio file.
        page: Flet page instance.

    Returns:
        A Container with play and download buttons.
    """
    _ = page  # Reserved for future use.

    async def on_play(_e: ft.ControlEvent) -> None:
        """Open audio in a new browser tab for native playback."""
        logger.debug("Play requested: %s", audio_url)
        try:
            await UrlLauncher().launch_url(audio_url)
        except Exception:
            logger.exception("Failed to launch audio URL")

    async def on_download(_e: ft.ControlEvent) -> None:
        """Open the audio URL to trigger download."""
        logger.debug("Download requested: %s", audio_url)
        try:
            await UrlLauncher().launch_url(audio_url)
        except Exception:
            logger.exception("Failed to launch download URL")

    play_btn = ft.ElevatedButton(
        content=ft.Row(
            controls=[
                ft.Icon(icon=ft.Icons.PLAY_ARROW, color=PRIMARY, size=20),
                ft.Text(
                    "Play Audio",
                    size=14,
                    font_family="Inter",
                    weight=ft.FontWeight.W_600,
                    color=PRIMARY,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=SPACING_SM,
        ),
        bgcolor=ACCENT_GOLD,
        on_click=on_play,
    )

    download_btn = ft.ElevatedButton(
        content=ft.Row(
            controls=[
                ft.Icon(icon=ft.Icons.DOWNLOAD, color=ON_SURFACE, size=20),
                ft.Text(
                    "Download",
                    size=14,
                    font_family="Inter",
                    weight=ft.FontWeight.W_600,
                    color=ON_SURFACE,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=SPACING_SM,
        ),
        bgcolor=SURFACE_DIM,
        on_click=on_download,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(width=_MAX_WIDTH, height=1, bgcolor=DIVIDER),
                ft.Container(height=SPACING_MD),
                ft.Row(
                    controls=[play_btn, download_btn],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=SPACING_LG,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        border_radius=_BORDER_RADIUS,
        padding=SPACING_MD,
        width=_MAX_WIDTH,
    )
