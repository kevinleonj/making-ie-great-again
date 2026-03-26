"""Route handling for the Flet frontend.

Maps URL routes to their corresponding page builders and constructs
views with the shared navigation bar and scrollable content area.
"""

from __future__ import annotations

import logging

import flet as ft

from frontend.components.nav_bar import build_nav_bar
from frontend.pages import architecture, bio_maduro, bio_trump, home
from frontend.theme import SURFACE

logger = logging.getLogger(__name__)

# Maps route strings to their page builder modules.
_ROUTE_BUILDERS: dict[str, object] = {
    "/": home,
    "/bio/trump": bio_trump,
    "/bio/maduro": bio_maduro,
    "/architecture": architecture,
}


def build_view(page: ft.Page, route: str) -> ft.View:
    """Build the appropriate view for a given route.

    Wraps each page's content in a consistent layout with the shared
    navigation bar at the top and a scrollable content column below.

    Args:
        page: The Flet page instance (used for navigation context).
        route: The URL route string to resolve.

    Returns:
        A ``ft.View`` matching the requested route.
    """
    resolved_route = route if route in _ROUTE_BUILDERS else "/"
    builder_module = _ROUTE_BUILDERS[resolved_route]
    page_controls: list[ft.Control] = builder_module.build(page)  # type: ignore[attr-defined]

    logger.debug("Building view for route: %s", resolved_route)

    return ft.View(
        route=resolved_route,
        bgcolor=SURFACE,
        padding=0,
        spacing=0,
        controls=[
            build_nav_bar(page, resolved_route),
            ft.Column(
                controls=page_controls,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
    )
