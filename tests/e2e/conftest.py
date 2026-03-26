"""E2E test fixtures with Playwright browser."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

# Ensure test-results directory exists
_RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "test-results"
_RESULTS_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def _check_servers(frontend_url: str, backend_url: str) -> None:
    """Skip all E2E tests if servers aren't running."""
    errors: list[str] = []
    try:
        httpx.get(frontend_url, timeout=5.0)
    except (httpx.ConnectError, httpx.TimeoutException):
        errors.append(f"Frontend not available at {frontend_url}")

    try:
        httpx.get(f"{backend_url}/api/health", timeout=5.0)
    except (httpx.ConnectError, httpx.TimeoutException):
        errors.append(f"Backend not available at {backend_url}")

    if errors:
        pytest.skip("; ".join(errors))


@pytest.fixture()
def results_dir() -> Path:
    """Path to test results directory for screenshots."""
    return _RESULTS_DIR
