"""Architecture overview page explaining the system pipeline and technology stack."""

from __future__ import annotations

import flet as ft

from frontend.components.page_header import build_page_header
from frontend.theme import (
    ACCENT_GOLD,
    DIVIDER,
    ON_SURFACE,
    SPACING_LG,
    SPACING_MD,
    SPACING_XL,
    SPACING_XXL,
    SURFACE_DIM,
    body_text,
    heading_text,
    subheading_text,
)


def _build_pipeline_section() -> ft.Container:
    """Build the pipeline explanation section with numbered steps.

    Returns:
        A Container with the numbered pipeline steps.
    """
    steps = [
        "User types text in the frontend interface",
        "Text is sent to the FastAPI backend via HTTP",
        ("Claude API transforms the text into the selected leader's speaking style and language"),
        "The transformed text is sent to fal.ai F5-TTS for voice synthesis via cloud API",
        "Generated WAV audio is returned to the frontend for playback",
    ]

    step_controls: list[ft.Control] = [
        heading_text("Pipeline"),
        ft.Container(height=SPACING_MD),
    ]

    for idx, step_text in enumerate(steps, start=1):
        step_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        value=str(idx),
                        size=18,
                        font_family="Playfair Display",
                        weight=ft.FontWeight.BOLD,
                        color=ACCENT_GOLD,
                    ),
                    width=36,
                    height=36,
                    border_radius=18,
                    border=ft.border.all(2, ACCENT_GOLD),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(width=SPACING_MD),
                ft.Container(
                    content=body_text(step_text),
                    expand=True,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        step_controls.append(step_row)
        step_controls.append(ft.Container(height=SPACING_MD))

    return ft.Container(
        content=ft.Column(controls=step_controls, spacing=0),
        padding=ft.Padding.symmetric(horizontal=SPACING_XXL, vertical=SPACING_LG),
    )


def _build_tech_stack_section() -> ft.Container:
    """Build the technology stack section.

    Returns:
        A Container with the technology stack listing.
    """
    stack_items = [
        ("Frontend", "Flet 0.80.5 (Python)"),
        ("Backend", "FastAPI (Python)"),
        ("LLM", "Claude API (Anthropic)"),
        ("TTS", "fal.ai F5-TTS (cloud API)"),
        ("Communication", "HTTP / REST"),
    ]

    stack_controls: list[ft.Control] = [
        heading_text("Technology Stack"),
        ft.Container(height=SPACING_MD),
    ]

    for label, description in stack_items:
        item_row = ft.Row(
            controls=[
                ft.Container(
                    content=subheading_text(label, color=ACCENT_GOLD),
                    width=180,
                ),
                body_text(description),
            ],
            spacing=SPACING_MD,
        )
        stack_controls.append(item_row)
        stack_controls.append(
            ft.Container(
                height=1,
                bgcolor=DIVIDER,
                margin=ft.Margin.symmetric(vertical=SPACING_MD // 2),
            ),
        )

    return ft.Container(
        content=ft.Column(controls=stack_controls, spacing=0),
        bgcolor=SURFACE_DIM,
        border_radius=12,
        padding=SPACING_LG,
        margin=ft.Margin.symmetric(horizontal=SPACING_XXL),
    )


def build(page: ft.Page) -> list[ft.Control]:
    """Build the architecture explanation page controls.

    Args:
        page: Flet page (reserved for future interactivity).

    Returns:
        A list of controls composing the architecture page.
    """
    _ = page  # Reserved for future use.

    header = build_page_header(
        title="System Architecture",
        subtitle="How MakingIEGreatAgain Works",
    )

    pipeline = _build_pipeline_section()
    tech_stack = _build_tech_stack_section()

    # Placeholder slot for future architecture diagram embed.
    embed_slot = ft.Container(
        key="embed_slot",
        height=400,
        bgcolor=SURFACE_DIM,
        border_radius=12,
        alignment=ft.Alignment.CENTER,
        content=body_text("[Architecture diagram placeholder]", color=ON_SURFACE),
        margin=ft.Margin.symmetric(
            horizontal=SPACING_XXL,
            vertical=SPACING_XL,
        ),
    )

    return [header, pipeline, tech_stack, embed_slot]
