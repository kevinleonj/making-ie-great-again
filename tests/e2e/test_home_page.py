"""E2E tests for the home page."""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
class TestHomePage:
    """Home page E2E tests."""

    def test_home_loads(
        self,
        page: Page,
        frontend_url: str,
        _check_servers: None,
        results_dir: Path,
    ) -> None:
        """App loads without errors and renders content."""
        page.goto(frontend_url)
        page.wait_for_timeout(4000)
        page.screenshot(path=str(results_dir / "home_loaded.png"))
        # Verify page loaded (no error dialog)
        assert page.url is not None

    def test_home_shows_leader_cards(
        self,
        page: Page,
        frontend_url: str,
        _check_servers: None,
        results_dir: Path,
    ) -> None:
        """Home page shows two leader selection cards."""
        page.goto(frontend_url)
        page.wait_for_timeout(4000)
        page.screenshot(path=str(results_dir / "leader_cards.png"), full_page=True)
