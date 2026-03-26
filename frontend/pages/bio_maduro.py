"""Maduro biography page view with portrait, biography, and key facts."""

from __future__ import annotations

import flet as ft

from frontend.components.page_header import build_page_header
from frontend.theme import (
    ACCENT_GOLD,
    DIVIDER,
    SPACING_LG,
    SPACING_MD,
    SPACING_XL,
    SPACING_XXL,
    SURFACE_DIM,
    body_text,
    heading_text,
    subheading_text,
)


def _build_portrait() -> ft.Container:
    """Build the Maduro official portrait container.

    Returns:
        A Container with the Maduro portrait image at 400x500 pixels.
    """
    return ft.Container(
        width=400,
        height=500,
        border_radius=12,
        border=ft.border.all(1, DIVIDER),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        image=ft.DecorationImage(
            src="Maduro.jpg",
            fit=ft.BoxFit.COVER,
            alignment=ft.Alignment.TOP_CENTER,
        ),
    )


def _build_biography_section() -> ft.Column:
    """Build the biography text section.

    Returns:
        A Column of biography paragraphs.
    """
    paragraphs = [
        (
            "Nicolas Maduro Moros was born on November 23, 1962, in Caracas,"
            " Venezuela. Before entering politics, he worked as a bus driver"
            " and became active in the transportation workers' union, where he"
            " developed his skills as an organizer and public speaker."
        ),
        (
            "Maduro rose through Venezuelan politics under the mentorship of"
            " Hugo Chavez, the charismatic leader of the Bolivarian Revolution."
            " He served in the National Assembly and held key diplomatic and"
            " political roles, building a reputation as a loyal and capable"
            " representative of the Chavista movement."
        ),
        (
            "From 2006 to 2013, Maduro served as Venezuela's Minister of Foreign"
            " Affairs, representing the country on the international stage and"
            " strengthening alliances with other left leaning Latin American"
            " governments and nations in the Global South."
        ),
        (
            "When Chavez passed away in March 2013, Maduro was selected as his"
            " successor. He won the presidential election in April 2013 and has"
            " served as President of Venezuela since then, continuing the"
            " Bolivarian Revolution's social and economic policies."
        ),
        (
            "Maduro is known for his distinctive communication style:"
            " revolutionary rhetoric, frequent references to Chavez and Simon"
            " Bolivar, anti imperialist framing of domestic and foreign policy,"
            " and emotional crescendos in his speeches. He often invokes the"
            " legacy of the revolution to rally popular support."
        ),
    ]

    controls: list[ft.Control] = [heading_text("Biography")]
    controls.append(ft.Container(height=SPACING_MD))

    for paragraph in paragraphs:
        controls.append(body_text(paragraph))
        controls.append(ft.Container(height=SPACING_MD))

    return ft.Column(controls=controls, spacing=0)


def _build_key_facts_section() -> ft.Container:
    """Build the key facts card.

    Returns:
        A styled container with key biographical facts.
    """
    facts = [
        ("Full Name", "Nicolas Maduro Moros"),
        ("Born", "November 23, 1962"),
        ("Birthplace", "Caracas, Venezuela"),
        ("Party", "United Socialist Party of Venezuela (PSUV)"),
        (
            "Communication Style",
            "Revolutionary rhetoric, Bolivarian references, emotional appeals",
        ),
    ]

    fact_controls: list[ft.Control] = [
        subheading_text("Key Facts", color=ACCENT_GOLD),
        ft.Container(height=SPACING_MD),
    ]

    for label, value in facts:
        fact_controls.append(
            ft.Row(
                controls=[
                    ft.Container(
                        content=body_text(f"{label}:", color=ACCENT_GOLD),
                        width=200,
                    ),
                    body_text(value),
                ],
                spacing=SPACING_MD,
            ),
        )
        fact_controls.append(ft.Container(height=SPACING_MD // 2))

    return ft.Container(
        content=ft.Column(controls=fact_controls, spacing=0),
        bgcolor=SURFACE_DIM,
        border_radius=12,
        padding=SPACING_LG,
        margin=ft.Margin.only(top=SPACING_XL),
    )


def build(page: ft.Page) -> list[ft.Control]:
    """Build the Maduro biography page controls.

    Args:
        page: Flet page (reserved for future interactivity).

    Returns:
        A list of controls composing the Maduro biography page.
    """
    _ = page  # Reserved for future use.

    header = build_page_header(
        title="Nicolas Maduro",
        subtitle="President of Venezuela",
    )

    portrait = _build_portrait()
    bio_section = _build_biography_section()
    facts_section = _build_key_facts_section()

    right_column = ft.Column(
        controls=[bio_section, facts_section],
        spacing=0,
        expand=True,
    )

    content_row = ft.Container(
        content=ft.Row(
            controls=[portrait, right_column],
            spacing=SPACING_XXL,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        ),
        padding=ft.Padding.symmetric(horizontal=SPACING_XXL, vertical=SPACING_LG),
    )

    return [header, content_row]
