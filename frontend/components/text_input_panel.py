"""Text input panel component with transform button and result display."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import flet as ft

from frontend.theme import (
    ACCENT_GOLD,
    DIVIDER,
    ON_SURFACE,
    PRIMARY,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SURFACE_DIM,
    body_text,
    caption_text,
    subheading_text,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------

_MAX_WIDTH = 600
_BORDER_RADIUS = 8
_QUOTE_BORDER_WIDTH = 4
_TEXTFIELD_MIN_LINES = 3
_TEXTFIELD_MAX_LINES = 8
_PROGRESS_RING_SIZE = 20
_PROGRESS_RING_STROKE = 2


def build_text_input_panel(
    leader_name: str,
    on_text_change: Callable[[str], None],
    on_transform: Callable[[], Any],
    current_text: str,
    transformed_text: str,
    is_transforming: bool,
    max_length: int,
) -> ft.Container:
    """Build the text input panel with transform button and result display.

    Args:
        leader_name: Currently selected leader name.
        on_text_change: Callback when text changes.
        on_transform: Callback when transform button is clicked.
        current_text: Current input text.
        transformed_text: Transformed text result (empty if not yet transformed).
        is_transforming: Whether transformation is in progress.
        max_length: Maximum allowed input length.

    Returns:
        A Container with text input, character counter, transform button, and result.
    """

    # -- Transform click handler ---------------------------------------------
    async def handle_transform(_e: ft.ControlEvent) -> None:
        """Delegate to the on_transform callback."""
        logger.debug("Transform button clicked for leader: %s", leader_name)
        result = on_transform()
        if hasattr(result, "__await__"):
            await result

    # -- Character counter ---------------------------------------------------
    char_count = len(current_text)
    counter_label = caption_text(f"{char_count}/{max_length}")
    counter_row = ft.Row(
        controls=[counter_label],
        alignment=ft.MainAxisAlignment.END,
    )

    # -- Transform button with optional progress ring ------------------------
    button_disabled = len(current_text.strip()) == 0 or is_transforming

    button_content_controls: list[ft.Control] = []
    if is_transforming:
        button_content_controls.append(
            ft.ProgressRing(
                width=_PROGRESS_RING_SIZE,
                height=_PROGRESS_RING_SIZE,
                stroke_width=_PROGRESS_RING_STROKE,
                color=PRIMARY,
            )
        )
        button_content_controls.append(ft.Container(width=SPACING_SM))

    button_content_controls.append(
        ft.Text(
            value="TRANSFORM TEXT",
            size=14,
            font_family="Inter",
            weight=ft.FontWeight.W_600,
            color=PRIMARY,
        )
    )

    transform_button = ft.Button(
        content=ft.Row(
            controls=button_content_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
        ),
        bgcolor=ACCENT_GOLD,
        disabled=button_disabled,
        on_click=handle_transform,
    )

    # -- Text change handler -------------------------------------------------
    def handle_text_change(e: ft.ControlEvent) -> None:
        """Forward text changes, enforcing max length."""
        value = e.control.value or ""
        if len(value) > max_length:
            value = value[:max_length]
            e.control.value = value
            e.control.update()
        on_text_change(value)
        # Update counter and button state in-place (no rebuild needed)
        counter_label.value = f"{len(value)}/{max_length}"
        counter_label.update()
        transform_button.disabled = len(value.strip()) == 0 or is_transforming
        transform_button.update()

    # -- Text input field ----------------------------------------------------
    text_field = ft.TextField(
        value=current_text,
        multiline=True,
        min_lines=_TEXTFIELD_MIN_LINES,
        max_lines=_TEXTFIELD_MAX_LINES,
        hint_text=f"Type what you want {leader_name} to say...",
        border_color=DIVIDER,
        focused_border_color=ACCENT_GOLD,
        on_change=handle_text_change,
    )

    button_row = ft.Row(
        controls=[transform_button],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # -- Build controls list -------------------------------------------------
    controls: list[ft.Control] = [
        subheading_text(f"What should {leader_name} say?"),
        ft.Container(height=SPACING_MD),
        text_field,
        counter_row,
        ft.Container(height=SPACING_MD),
        button_row,
    ]

    # -- Transformed text display (quote style) ------------------------------
    if transformed_text:
        quote_container = ft.Container(
            content=body_text(transformed_text, color=ON_SURFACE),
            bgcolor=SURFACE_DIM,
            padding=SPACING_MD,
            border=ft.border.only(
                left=ft.BorderSide(_QUOTE_BORDER_WIDTH, ACCENT_GOLD),
            ),
            border_radius=ft.BorderRadius.only(
                top_right=_BORDER_RADIUS,
                bottom_right=_BORDER_RADIUS,
            ),
        )
        controls.append(ft.Container(height=SPACING_LG))
        controls.append(quote_container)

    # -- Wrap in outer container ---------------------------------------------
    return ft.Container(
        content=ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        width=_MAX_WIDTH,
        padding=SPACING_LG,
        alignment=ft.Alignment.CENTER,
    )
