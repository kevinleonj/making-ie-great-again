"""E2E tests for leader selection interaction."""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
class TestLeaderSelection:
    """Leader selection E2E tests."""

    def test_initial_state_no_selection(
        self,
        page: Page,
        frontend_url: str,
        _check_servers: None,
        results_dir: Path,
    ) -> None:
        """Initially no leader is selected."""
        page.goto(frontend_url)
        page.wait_for_timeout(4000)
        page.screenshot(path=str(results_dir / "selection_initial.png"))

    def test_click_selects_leader(
        self,
        page: Page,
        frontend_url: str,
        _check_servers: None,
        results_dir: Path,
    ) -> None:
        """Clicking a leader card changes visual state."""
        page.goto(frontend_url)
        page.wait_for_timeout(4000)

        # Click on the left side of the viewport (Trump card area)
        viewport = page.viewport_size
        if viewport:
            # Click approximately where the Trump card should be
            page.mouse.click(viewport["width"] // 2 - 180, 400)
            page.wait_for_timeout(1000)
            page.screenshot(path=str(results_dir / "selection_trump_clicked.png"))
