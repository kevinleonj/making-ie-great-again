"""Reusable page header component with title, optional subtitle, and gold divider."""

from __future__ import annotations

import flet as ft

from frontend.theme import (
    ACCENT_GOLD,
    SPACING_LG,
    SPACING_MD,
    SPACING_XXL,
    display_text,
    subheading_text,
)


def build_page_header(title: str, subtitle: str | None = None) -> ft.Container:
    """Build a centered page header with title, optional subtitle, and gold divider.

    Args:
        title: The main header title text.
        subtitle: Optional subtitle displayed below the title.

    Returns:
        A Container with centered title, optional subtitle, and gold accent divider.
    """
    controls: list[ft.Control] = [display_text(title)]

    if subtitle is not None:
        controls.append(ft.Container(height=SPACING_MD))
        controls.append(subheading_text(subtitle))

    # Gold divider line.
    controls.append(ft.Container(height=SPACING_MD))
    controls.append(
        ft.Container(
            width=80,
            height=3,
            bgcolor=ACCENT_GOLD,
            border_radius=2,
        ),
    )

    header_column = ft.Column(
        controls=controls,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    return ft.Container(
        content=header_column,
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=SPACING_XXL, bottom=SPACING_LG),
    )
