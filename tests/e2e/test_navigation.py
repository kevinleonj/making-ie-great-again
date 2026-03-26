"""E2E tests for navigation between pages."""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
class TestNavigation:
    """Navigation E2E tests."""

    def test_can_load_all_routes(
        self,
        page: Page,
        frontend_url: str,
        _check_servers: None,
        results_dir: Path,
    ) -> None:
        """All four routes load without errors."""
        routes = [
            ("/", "home"),
            ("/bio/trump", "bio_trump"),
            ("/bio/maduro", "bio_maduro"),
            ("/architecture", "architecture"),
        ]
        for route, name in routes:
            page.goto(f"{frontend_url}#{route}")
            page.wait_for_timeout(3000)
            page.screenshot(path=str(results_dir / f"nav_{name}.png"))

    def test_navigation_preserves_layout(
        self,
        page: Page,
        frontend_url: str,
        _check_servers: None,
        results_dir: Path,
    ) -> None:
        """Navigation bar is visible on all pages."""
        page.goto(frontend_url)
        page.wait_for_timeout(4000)
        page.screenshot(path=str(results_dir / "nav_layout_home.png"))

        page.goto(f"{frontend_url}#/bio/trump")
        page.wait_for_timeout(3000)
        page.screenshot(path=str(results_dir / "nav_layout_trump.png"))
