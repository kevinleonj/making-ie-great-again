"""Top navigation bar component for the MakingIEGreatAgain application."""

from __future__ import annotations

import logging

import flet as ft

from frontend.theme import ACCENT_GOLD, ON_PRIMARY, PRIMARY, SPACING_LG

logger = logging.getLogger(__name__)

# Route definitions for navigation items.
_NAV_ITEMS: list[tuple[str, str]] = [
    ("Home", "/"),
    ("Trump", "/bio/trump"),
    ("Maduro", "/bio/maduro"),
    ("Architecture", "/architecture"),
]


def build_nav_bar(page: ft.Page, active_route: str) -> ft.Container:
    """Build the top navigation bar.

    Args:
        page: Flet page for navigation.
        active_route: Current active route for highlighting.

    Returns:
        A Container wrapping the navigation row.
    """

    def _make_nav_click_handler(route: str):  # noqa: ANN202
        """Create an async click handler for a nav item.

        Args:
            route: The route to navigate to on click.

        Returns:
            An async event handler function.
        """

        async def on_nav_click(e: ft.ControlEvent) -> None:
            logger.debug("Navigating to %s", route)
            await page.push_route(route)

        return on_nav_click

    nav_buttons: list[ft.Control] = []
    for label, route in _NAV_ITEMS:
        is_active = active_route == route
        nav_buttons.append(
            ft.TextButton(
                content=ft.Text(
                    value=label,
                    size=15,
                    font_family="Inter",
                    weight=ft.FontWeight.W_500,
                    color=ACCENT_GOLD if is_active else ON_PRIMARY,
                    opacity=1.0 if is_active else 0.7,
                ),
                on_click=_make_nav_click_handler(route),
            ),
        )

    brand = ft.Text(
        value="MakingIEGreatAgain",
        font_family="Playfair Display",
        size=22,
        weight=ft.FontWeight.BOLD,
        color=ACCENT_GOLD,
    )

    nav_row = ft.Row(
        controls=[
            brand,
            ft.Row(controls=nav_buttons, spacing=4),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    return ft.Container(
        content=nav_row,
        bgcolor=PRIMARY,
        height=64,
        padding=ft.padding.symmetric(horizontal=SPACING_LG),
    )
