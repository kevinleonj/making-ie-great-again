"""Trump biography page view with portrait, biography, and key facts."""

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
    """Build the Trump official portrait container.

    Returns:
        A Container with the Trump portrait image at 400x500 pixels.
    """
    return ft.Container(
        width=400,
        height=500,
        border_radius=12,
        border=ft.border.all(1, DIVIDER),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Image(
            src="Trump.jpg",
            width=400,
            height=500,
            fit=ft.BoxFit.COVER,
        ),
    )


def _build_biography_section() -> ft.Column:
    """Build the biography text section.

    Returns:
        A Column of biography paragraphs.
    """
    paragraphs = [
        (
            "Donald John Trump was born on June 14, 1946, in Queens, New York City."
            " The son of real estate developer Fred Trump, he grew up immersed in"
            " the world of property development and business negotiation from an"
            " early age."
        ),
        (
            "After graduating from the Wharton School of the University of"
            " Pennsylvania in 1968, Trump joined his father's company, eventually"
            " renaming it The Trump Organization. Under his leadership, the company"
            " expanded into luxury real estate, hotels, casinos, and golf courses"
            " across the globe."
        ),
        (
            "Trump became a household name through his role as host of the NBC"
            ' reality television show "The Apprentice," which aired from 2004'
            ' to 2015. His catchphrase "You\'re fired" became iconic in American'
            " popular culture."
        ),
        (
            "In 2016, Trump won the presidential election, becoming the 45th"
            " President of the United States. He served from 2017 to 2021,"
            " then won the presidency again in 2024, becoming the 47th President"
            " in January 2025."
        ),
        (
            "Trump is known for his distinctive communication style:"
            " heavy use of superlatives, repetition for emphasis, simple and"
            ' direct vocabulary, and signature phrases like "believe me,"'
            ' "tremendous," and "the best." His speaking pattern often'
            " features short, declarative sentences and personal asides."
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
        ("Full Name", "Donald John Trump"),
        ("Born", "June 14, 1946"),
        ("Birthplace", "Queens, New York City"),
        ("Party", "Republican"),
        (
            "Communication Style",
            "Direct, superlative heavy, repetitive for emphasis",
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
    """Build the Trump biography page controls.

    Args:
        page: Flet page (reserved for future interactivity).

    Returns:
        A list of controls composing the Trump biography page.
    """
    _ = page  # Reserved for future use.

    header = build_page_header(
        title="Donald Trump",
        subtitle="45th and 47th President of the United States",
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
