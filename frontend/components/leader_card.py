"""Leader selection card component for choosing a voice leader."""

from __future__ import annotations

import logging
from collections.abc import Callable

import flet as ft

from frontend.theme import (
    ACCENT_GOLD,
    ACCENT_GOLD_LIGHT,
    DIVIDER,
    ON_SURFACE,
    SPACING_LG,
    SPACING_MD,
    SURFACE,
    caption_text,
    heading_text,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Card dimensions
# ---------------------------------------------------------------------------

_CARD_WIDTH = 280
_PORTRAIT_WIDTH = 240
_PORTRAIT_HEIGHT = 300
_BORDER_RADIUS = 12
_PORTRAIT_RADIUS = 8
_SHADOW_BLUR_UNSELECTED = 4
_SHADOW_BLUR_SELECTED = 12
_BORDER_UNSELECTED = 1
_BORDER_SELECTED = 3


def build_leader_card(
    name: str,
    language_label: str,
    is_selected: bool,
    on_select: Callable[[], None],
) -> ft.Container:
    """Build a clickable leader selection card.

    Args:
        name: Leader name ("Donald Trump" or "Nicolas Maduro").
        language_label: Language tag ("English" or "Espanol").
        is_selected: Whether this card is currently selected.
        on_select: Callback when card is clicked.

    Returns:
        A styled Container acting as a selectable card.
    """
    # -- Portrait image ------------------------------------------------------
    image_file = name.split()[-1] + ".jpg"
    portrait = ft.Container(
        width=_PORTRAIT_WIDTH,
        height=_PORTRAIT_HEIGHT,
        border_radius=_PORTRAIT_RADIUS,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        opacity=1.0 if is_selected else 0.6,
        image=ft.DecorationImage(
            src=image_file,
            fit=ft.BoxFit.COVER,
            alignment=ft.Alignment.TOP_CENTER,
        ),
    )

    # -- Name and language labels --------------------------------------------
    name_label = heading_text(
        name,
        color=ACCENT_GOLD if is_selected else ON_SURFACE,
    )
    lang_label = caption_text(language_label)

    # -- Card content column -------------------------------------------------
    card_column = ft.Column(
        controls=[
            portrait,
            ft.Container(height=SPACING_MD),
            name_label,
            lang_label,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    # -- Border and shadow based on selection state --------------------------
    if is_selected:
        border = ft.border.all(_BORDER_SELECTED, ACCENT_GOLD)
        shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=_SHADOW_BLUR_SELECTED,
            color=ACCENT_GOLD_LIGHT,
            offset=ft.Offset(0, 2),
        )
        bg_color = SURFACE
    else:
        border = ft.border.all(_BORDER_UNSELECTED, DIVIDER)
        shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=_SHADOW_BLUR_UNSELECTED,
            color=DIVIDER,
            offset=ft.Offset(0, 1),
        )
        bg_color = SURFACE

    # -- Hover handler -------------------------------------------------------
    def on_hover(e: ft.ControlEvent) -> None:
        """Change border on hover when card is not selected."""
        if is_selected:
            return
        if e.data == "true":
            e.control.border = ft.border.all(_BORDER_UNSELECTED, ACCENT_GOLD_LIGHT)
        else:
            e.control.border = ft.border.all(_BORDER_UNSELECTED, DIVIDER)
        e.control.update()

    # -- Click handler wrapper -----------------------------------------------
    def on_click(_e: ft.ControlEvent) -> None:
        """Delegate to the on_select callback."""
        logger.debug("Leader card clicked: %s", name)
        on_select()

    # -- Assemble card container ---------------------------------------------
    return ft.Container(
        content=card_column,
        width=_CARD_WIDTH,
        padding=SPACING_LG,
        border=border,
        border_radius=_BORDER_RADIUS,
        bgcolor=bg_color,
        shadow=shadow,
        on_click=on_click,
        on_hover=on_hover,
    )
