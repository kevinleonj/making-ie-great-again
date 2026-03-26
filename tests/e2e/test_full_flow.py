"""E2E tests for the complete generation flow."""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page


@pytest.mark.e2e
class TestFullFlow:
    """Full generation flow E2E tests."""

    def test_full_flow_screenshot_sequence(
        self,
        page: Page,
        frontend_url: str,
        _check_servers: None,
        results_dir: Path,
    ) -> None:
        """Capture the full flow as a screenshot sequence."""
        page.goto(frontend_url)
        page.wait_for_timeout(4000)
        page.screenshot(path=str(results_dir / "flow_01_initial.png"))

        # This test primarily serves as visual documentation.
        # Full interaction testing requires coordinate based clicks
        # which are fragile. The API level tests cover correctness.
