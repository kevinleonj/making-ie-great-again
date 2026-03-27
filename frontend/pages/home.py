"""Home page view with leader selection, text input, and audio controls."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import flet as ft

from frontend.api_client import get_api_client
from frontend.components.audio_player import build_audio_player
from frontend.components.leader_card import build_leader_card
from frontend.components.page_header import build_page_header
from frontend.components.text_input_panel import build_text_input_panel
from frontend.config import get_settings
from frontend.theme import (
    ACCENT_GOLD,
    DIVIDER,
    ERROR,
    ON_PRIMARY,
    ON_SURFACE,
    PRIMARY,
    SPACING_LG,
    SPACING_MD,
    SPACING_XL,
    SPACING_XXL,
    caption_text,
)

logger = logging.getLogger(__name__)

_AUDIO_SECTION_WIDTH = 400

_LEADERS: dict[str, dict[str, str]] = {
    "trump": {"name": "Donald Trump", "language": "English"},
    "maduro": {"name": "Nicolas Maduro", "language": "Espanol"},
}


@dataclass
class HomeState:
    """Mutable state for the home page."""

    selected_leader: str | None = None
    input_text: str = ""
    transformed_text: str = ""
    is_transforming: bool = False
    is_generating: bool = False
    audio_url: str | None = None
    error_message: str | None = None
    max_input_length: int = field(
        default_factory=lambda: get_settings().max_input_length,
    )


def build(page: ft.Page) -> list[ft.Control]:
    """Build the home page with leader selection, text input, and audio controls.

    Args:
        page: The Flet page instance.

    Returns:
        A list containing the self-updating content column.
    """
    state = HomeState()

    content_column = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        spacing=0,
    )

    # -- Callbacks -----------------------------------------------------------

    def select_leader(leader_key: str) -> None:
        """Update selected leader and reset text state."""
        logger.debug("Leader selected: %s", leader_key)
        state.selected_leader = leader_key
        state.input_text = ""
        state.transformed_text = ""
        state.error_message = None
        rebuild()

    def select_trump() -> None:
        """Select Trump as the active leader."""
        select_leader("trump")

    def select_maduro() -> None:
        """Select Maduro as the active leader."""
        select_leader("maduro")

    def on_text_change(text: str) -> None:
        """Handle text input changes."""
        state.input_text = text

    def on_transform() -> None:
        """Call /api/transform and update state with the result."""
        if not state.input_text.strip() or state.selected_leader is None:
            return
        state.is_transforming = True
        state.error_message = None
        rebuild()
        try:
            result = get_api_client().transform_text(state.selected_leader, state.input_text)
            state.transformed_text = result.transformed_text
        except Exception:
            logger.exception("Transform API call failed")
            state.error_message = (
                "Could not connect to the transformation service. "
                "Please check that the backend is running and try again."
            )
            state.transformed_text = ""
        finally:
            state.is_transforming = False
            rebuild()

    def on_generate_audio() -> None:
        """Call /api/tts and update state with the audio URL."""
        if not state.transformed_text or state.selected_leader is None:
            return
        state.is_generating = True
        state.error_message = None
        rebuild()
        try:
            client = get_api_client()
            result = client.generate_tts(state.selected_leader, state.transformed_text)
            state.audio_url = client.get_audio_url(result.audio_url)
        except Exception as exc:
            logger.exception("TTS API call failed")
            state.error_message = f"Audio generation failed: {exc}"
            state.audio_url = None
        finally:
            state.is_generating = False
            rebuild()

    # -- Zone builders -------------------------------------------------------

    def build_zone_1() -> ft.Container:
        """Build Zone 1: leader selection cards and status text."""
        trump_meta = _LEADERS["trump"]
        maduro_meta = _LEADERS["maduro"]

        trump_card = build_leader_card(
            name=trump_meta["name"],
            language_label=trump_meta["language"],
            is_selected=state.selected_leader == "trump",
            on_select=select_trump,
        )

        maduro_card = build_leader_card(
            name=maduro_meta["name"],
            language_label=maduro_meta["language"],
            is_selected=state.selected_leader == "maduro",
            on_select=select_maduro,
        )

        cards_row = ft.Row(
            controls=[trump_card, maduro_card],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=SPACING_XL,
        )

        # Status text
        if state.selected_leader and state.selected_leader in _LEADERS:
            leader_name = _LEADERS[state.selected_leader]["name"]
            status = caption_text(f"Selected: {leader_name}", color=ACCENT_GOLD)
        else:
            status = caption_text("Select a leader to begin", color=ON_SURFACE)

        return ft.Container(
            content=ft.Column(
                controls=[cards_row, ft.Container(height=SPACING_MD), status],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.only(bottom=SPACING_LG),
        )

    def build_zone_2() -> ft.Container:
        """Build Zone 2: text input panel (visible only when leader selected)."""
        if state.selected_leader is None:
            return ft.Container()

        leader_name = _LEADERS[state.selected_leader]["name"]

        panel = build_text_input_panel(
            leader_name=leader_name,
            on_text_change=on_text_change,
            on_transform=on_transform,
            current_text=state.input_text,
            transformed_text=state.transformed_text,
            is_transforming=state.is_transforming,
            max_length=state.max_input_length,
        )

        return ft.Container(
            content=panel,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.only(top=SPACING_LG, bottom=SPACING_LG),
        )

    def build_zone_3() -> ft.Container:
        """Build Zone 3: audio controls (visible only when text is transformed)."""
        if not state.transformed_text:
            return ft.Container()

        # Button content: optional spinner + label
        btn_parts: list[ft.Control] = []
        if state.is_generating:
            btn_parts.append(ft.ProgressRing(width=20, height=20, stroke_width=2, color=PRIMARY))
            btn_parts.append(ft.Container(width=8))
        btn_parts.append(
            ft.Text(
                "GENERATE AUDIO",
                size=16,
                font_family="Inter",
                weight=ft.FontWeight.W_600,
                color=PRIMARY,
            )
        )

        gen_btn = ft.Button(
            content=ft.Row(btn_parts, alignment=ft.MainAxisAlignment.CENTER, spacing=0),
            bgcolor=ACCENT_GOLD,
            disabled=state.is_generating,
            on_click=lambda _e: on_generate_audio(),
        )

        # Status text or audio player below button
        controls: list[ft.Control] = [
            ft.Container(width=_AUDIO_SECTION_WIDTH, height=1, bgcolor=DIVIDER),
            ft.Container(height=SPACING_MD),
            ft.Row([gen_btn], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=SPACING_MD),
        ]

        if state.audio_url:
            player = build_audio_player(state.audio_url, page)
            controls.append(player)
        elif not state.is_generating:
            controls.append(caption_text("Click to generate audio from the transformed text."))

        return ft.Container(
            content=ft.Column(
                controls=controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.only(bottom=SPACING_XXL),
        )

    # -- Rebuild function ----------------------------------------------------

    def _populate() -> None:
        """Populate the content column from current state."""
        # Remove previous audio controls from page overlay to prevent stacking
        page.overlay.clear()
        page.update()
        content_column.controls.clear()
        header = build_page_header(title="MakingIEGreatAgain", subtitle="Voice Cloning Demo")
        content_column.controls.extend([header, build_zone_1(), build_zone_2(), build_zone_3()])
        if state.error_message:
            content_column.controls.append(
                ft.Container(
                    content=ft.Text(state.error_message, color=ON_PRIMARY, size=14),
                    bgcolor=ERROR,
                    padding=SPACING_MD,
                    border_radius=8,
                    width=600,
                    alignment=ft.Alignment.CENTER,
                )
            )

    def rebuild() -> None:
        """Clear, rebuild, and push an update to the content column."""
        _populate()
        content_column.update()

    # -- Initial render ------------------------------------------------------

    _populate()
    return [content_column]
