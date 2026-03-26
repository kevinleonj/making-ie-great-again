"""Flet frontend entry point with theme, routing, and layout shell."""

from __future__ import annotations

import logging

import flet as ft

from frontend.config import get_settings
from frontend.router import build_view
from frontend.theme import (
    FONTS,
    build_dark_theme,
    build_light_theme,
)

logger = logging.getLogger(__name__)


def main(page: ft.Page) -> None:
    """Main Flet application entry point.

    Configures fonts, themes, routing, and renders the layout shell.

    Args:
        page: The root Flet page object.
    """
    settings = get_settings()

    # -- Fonts ---------------------------------------------------------------
    page.fonts = FONTS

    # -- Themes --------------------------------------------------------------
    page.theme = build_light_theme()
    page.dark_theme = build_dark_theme()
    page.theme_mode = ft.ThemeMode.LIGHT

    # -- Page metadata -------------------------------------------------------
    page.title = "MakingIEGreatAgain"
    page.padding = 0

    # -- Routing -------------------------------------------------------------
    def route_change() -> None:
        """Rebuild the view stack when the route changes."""
        page.views.clear()
        page.views.append(build_view(page, page.route))
        page.update()

    async def view_pop(e: ft.ViewPopEvent) -> None:
        """Handle the AppBar back button by popping the top view."""
        if e.view is not None:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Trigger initial render
    route_change()

    logger.info("Frontend started on port %d", settings.frontend_port)


if __name__ == "__main__":
    _settings = get_settings()
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=_settings.frontend_port)
