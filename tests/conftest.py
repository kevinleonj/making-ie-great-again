"""Shared test fixtures."""

from __future__ import annotations

import httpx
import pytest


@pytest.fixture(scope="session")
def backend_url() -> str:
    """Backend base URL."""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def frontend_url() -> str:
    """Frontend base URL."""
    return "http://localhost:8550"


@pytest.fixture(scope="session")
def backend_available(backend_url: str) -> bool:
    """Check if the backend is running."""
    try:
        resp = httpx.get(f"{backend_url}/api/health", timeout=5.0)
        return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


@pytest.fixture(scope="session")
def frontend_available(frontend_url: str) -> bool:
    """Check if the frontend is running."""
    try:
        resp = httpx.get(frontend_url, timeout=5.0)
        return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "e2e: end-to-end tests requiring running servers")
    config.addinivalue_line("markers", "integration: integration tests requiring backend")
