"""Color palette, typography helpers, and theme builders for the MakingIEGreatAgain UI."""

from __future__ import annotations

import flet as ft

from frontend.config import get_settings

# ---------------------------------------------------------------------------
# Color palette (defaults overridable via environment / .env)
# ---------------------------------------------------------------------------

_settings = get_settings()

PRIMARY: str = _settings.color_primary  # #000000
SURFACE: str = _settings.color_surface  # #FFFFFF
ON_SURFACE: str = _settings.color_on_surface  # #1A1A1A
ACCENT_GOLD: str = _settings.color_accent_gold  # #C5A572
ACCENT_GOLD_LIGHT: str = "#D4B98A"
ACCENT_GOLD_DARK: str = "#A8894F"
ERROR: str = "#B00020"
SURFACE_DIM: str = "#F5F5F0"
DIVIDER: str = "#E0D8CC"
ON_PRIMARY: str = "#FFFFFF"

# ---------------------------------------------------------------------------
# Font loading dict (passed to page.fonts)
# ---------------------------------------------------------------------------

FONTS: dict[str, str] = {
    "Playfair Display": (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/"
        "playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf"
    ),
    "Inter": (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf"
    ),
}

# ---------------------------------------------------------------------------
# Spacing constants (virtual pixels)
# ---------------------------------------------------------------------------

SPACING_XS: int = 4
SPACING_SM: int = 8
SPACING_MD: int = 16
SPACING_LG: int = 24
SPACING_XL: int = 32
SPACING_XXL: int = 48
SECTION_GAP: int = 64

# ---------------------------------------------------------------------------
# Typography helpers
# ---------------------------------------------------------------------------


def display_text(text: str, color: str | None = None) -> ft.Text:
    """Return a 36px bold Playfair Display text control.

    Args:
        text: The string content to display.
        color: Optional hex color override. Defaults to ON_SURFACE.

    Returns:
        A configured ``ft.Text`` control.
    """
    return ft.Text(
        value=text,
        size=36,
        font_family="Playfair Display",
        weight=ft.FontWeight.BOLD,
        color=color or ON_SURFACE,
    )


def heading_text(text: str, color: str | None = None) -> ft.Text:
    """Return a 28px semibold Playfair Display text control.

    Args:
        text: The string content to display.
        color: Optional hex color override. Defaults to ON_SURFACE.

    Returns:
        A configured ``ft.Text`` control.
    """
    return ft.Text(
        value=text,
        size=28,
        font_family="Playfair Display",
        weight=ft.FontWeight.W_600,
        color=color or ON_SURFACE,
    )


def subheading_text(text: str, color: str | None = None) -> ft.Text:
    """Return a 20px medium Inter text control.

    Args:
        text: The string content to display.
        color: Optional hex color override. Defaults to ON_SURFACE.

    Returns:
        A configured ``ft.Text`` control.
    """
    return ft.Text(
        value=text,
        size=20,
        font_family="Inter",
        weight=ft.FontWeight.W_500,
        color=color or ON_SURFACE,
    )


def body_text(text: str, color: str | None = None) -> ft.Text:
    """Return a 16px regular Inter text control.

    Args:
        text: The string content to display.
        color: Optional hex color override. Defaults to ON_SURFACE.

    Returns:
        A configured ``ft.Text`` control.
    """
    return ft.Text(
        value=text,
        size=16,
        font_family="Inter",
        weight=ft.FontWeight.NORMAL,
        color=color or ON_SURFACE,
    )


def caption_text(text: str, color: str | None = None) -> ft.Text:
    """Return a 12px regular Inter text control.

    Args:
        text: The string content to display.
        color: Optional hex color override. Defaults to ON_SURFACE.

    Returns:
        A configured ``ft.Text`` control.
    """
    return ft.Text(
        value=text,
        size=12,
        font_family="Inter",
        weight=ft.FontWeight.NORMAL,
        color=color or ON_SURFACE,
    )


# ---------------------------------------------------------------------------
# Theme builders
# ---------------------------------------------------------------------------


def build_light_theme() -> ft.Theme:
    """Build the light theme with a custom Material 3 ColorScheme.

    Returns:
        A ``ft.Theme`` configured for light mode with the gold accent palette.
    """
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ACCENT_GOLD,
            on_primary=PRIMARY,
            primary_container=ACCENT_GOLD_LIGHT,
            on_primary_container=PRIMARY,
            secondary=ON_SURFACE,
            on_secondary=ON_PRIMARY,
            surface=SURFACE,
            on_surface=ON_SURFACE,
            surface_dim=SURFACE_DIM,
            surface_container_highest=SURFACE_DIM,
            error=ERROR,
            on_error=ON_PRIMARY,
            outline=DIVIDER,
            outline_variant=DIVIDER,
            shadow=PRIMARY,
        ),
        font_family="Inter",
    )


def build_dark_theme() -> ft.Theme:
    """Build the dark theme variant with adjusted surface and accent tones.

    Returns:
        A ``ft.Theme`` configured for dark mode with the gold accent palette.
    """
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ACCENT_GOLD,
            on_primary="#FFFFFF",
            primary_container=ACCENT_GOLD_DARK,
            on_primary_container="#FFFFFF",
            secondary="#D4D4D4",
            on_secondary="#111111",
            surface="#111111",
            on_surface="#F5F5F0",
            surface_dim="#0A0A0A",
            surface_container_highest="#2A2A2A",
            error=ERROR,
            on_error="#FFFFFF",
            outline="#3A3A3A",
            outline_variant="#2A2A2A",
            shadow="#000000",
        ),
        font_family="Inter",
    )
