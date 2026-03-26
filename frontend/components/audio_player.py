"""Audio player component with playback controls and download button."""

from __future__ import annotations

import logging

import flet as ft
import flet_audio as fta

from frontend.theme import (
    ACCENT_GOLD,
    DIVIDER,
    ON_SURFACE,
    SPACING_MD,
    SPACING_SM,
    SURFACE_DIM,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------

_MAX_WIDTH = 600
_BORDER_RADIUS = 12
_ICON_SIZE = 28
_PROGRESS_TEXT_SIZE = 14
_DOWNLOAD_TEXT_SIZE = 14


def _format_time(milliseconds: int) -> str:
    """Format milliseconds as m:ss.

    Args:
        milliseconds: Time in milliseconds (non-negative).

    Returns:
        Formatted time string like "0:00" or "2:15".
    """
    if milliseconds < 0:
        milliseconds = 0
    total_seconds = milliseconds // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def _duration_to_ms(duration: ft.Duration | None) -> int:
    """Convert an ft.Duration to milliseconds.

    Args:
        duration: A Duration object, or None.

    Returns:
        Total milliseconds, or 0 if duration is None.
    """
    if duration is None:
        return 0
    return duration.in_milliseconds


def build_audio_player(
    audio_url: str,
    page: ft.Page,
) -> ft.Container:
    """Build an inline audio player with play/pause and download.

    Creates a non-visual fta.Audio control (added to page.overlay) and
    returns a visible Container with playback controls and a download
    button.

    Args:
        audio_url: Full URL to the WAV audio file.
        page: Flet page (needed for adding audio control to overlay).

    Returns:
        A Container with playback controls and download button.
    """
    # -- Mutable playback state -----------------------------------------------

    current_position_ms: list[int] = [0]
    total_duration_ms: list[int] = [0]
    is_playing: list[bool] = [False]

    # -- UI controls that need updating ---------------------------------------

    play_icon = ft.Icon(
        name=ft.Icons.PLAY_ARROW,
        color=ACCENT_GOLD,
        size=_ICON_SIZE,
    )

    progress_text = ft.Text(
        value="0:00 / 0:00",
        size=_PROGRESS_TEXT_SIZE,
        font_family="Inter",
        color=ON_SURFACE,
    )

    volume_icon = ft.Icon(
        name=ft.Icons.VOLUME_UP,
        color=ACCENT_GOLD,
        size=_ICON_SIZE - 4,
    )

    # -- Event handlers -------------------------------------------------------

    def on_state_change(e: fta.AudioStateChangeEvent) -> None:
        """Update play/pause icon when audio state changes."""
        logger.debug("Audio state changed: %s", e.state)
        if e.state == fta.AudioState.PLAYING:
            is_playing[0] = True
            play_icon.name = ft.Icons.PAUSE
        elif e.state in (
            fta.AudioState.PAUSED,
            fta.AudioState.STOPPED,
            fta.AudioState.COMPLETED,
        ):
            is_playing[0] = False
            play_icon.name = ft.Icons.PLAY_ARROW
        try:
            play_icon.update()
        except Exception:
            logger.debug("Could not update play icon (control may not be mounted)")

    def on_position_change(e: fta.AudioPositionChangeEvent) -> None:
        """Update progress text with current position."""
        current_position_ms[0] = e.position
        pos_str = _format_time(e.position)
        dur_str = _format_time(total_duration_ms[0])
        progress_text.value = f"{pos_str} / {dur_str}"
        try:
            progress_text.update()
        except Exception:
            logger.debug("Could not update progress text (control may not be mounted)")

    def on_duration_change(e: fta.AudioDurationChangeEvent) -> None:
        """Update total duration when it becomes available."""
        total_duration_ms[0] = _duration_to_ms(e.duration)
        dur_str = _format_time(total_duration_ms[0])
        pos_str = _format_time(current_position_ms[0])
        progress_text.value = f"{pos_str} / {dur_str}"
        logger.debug("Audio duration: %s ms", total_duration_ms[0])
        try:
            progress_text.update()
        except Exception:
            logger.debug("Could not update progress text (control may not be mounted)")

    # -- Audio control (non-visual, added to page overlay) --------------------

    audio = fta.Audio(
        src=audio_url,
        autoplay=False,
        volume=1.0,
        release_mode=fta.ReleaseMode.STOP,
        on_state_change=on_state_change,
        on_position_change=on_position_change,
        on_duration_change=on_duration_change,
    )

    page.overlay.append(audio)
    page.update()

    # -- Play/Pause click handler ---------------------------------------------

    async def on_play_pause(_e: ft.ControlEvent) -> None:
        """Toggle between play and pause."""
        try:
            if is_playing[0]:
                await audio.pause()
            else:
                await audio.play()
        except Exception:
            logger.exception("Playback control error")

    # -- Download click handler -----------------------------------------------

    def on_download(_e: ft.ControlEvent) -> None:
        """Open the audio URL to trigger download."""
        logger.debug("Download requested: %s", audio_url)
        page.launch_url(audio_url)

    # -- Visual layout --------------------------------------------------------

    play_pause_button = ft.IconButton(
        content=play_icon,
        on_click=on_play_pause,
        style=ft.ButtonStyle(padding=ft.padding.all(SPACING_SM)),
    )

    row_1 = ft.Row(
        controls=[
            play_pause_button,
            ft.Container(width=SPACING_SM),
            progress_text,
            ft.Container(expand=True),
            volume_icon,
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    download_button = ft.TextButton(
        text="Download WAV",
        icon=ft.Icons.DOWNLOAD,
        icon_color=ACCENT_GOLD,
        on_click=on_download,
        style=ft.ButtonStyle(
            color=ACCENT_GOLD,
            side=ft.BorderSide(width=1, color=ACCENT_GOLD),
            padding=ft.padding.symmetric(horizontal=SPACING_MD, vertical=SPACING_SM),
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    row_2 = ft.Row(
        controls=[download_button],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                row_1,
                ft.Container(
                    width=_MAX_WIDTH,
                    height=1,
                    bgcolor=DIVIDER,
                ),
                ft.Container(height=SPACING_SM),
                row_2,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=SPACING_SM,
        ),
        bgcolor=SURFACE_DIM,
        border_radius=_BORDER_RADIUS,
        padding=SPACING_MD,
        width=_MAX_WIDTH,
    )
