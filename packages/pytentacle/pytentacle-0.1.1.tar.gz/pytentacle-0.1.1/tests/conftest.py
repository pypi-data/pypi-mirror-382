"""Pytest configuration and fixtures."""

import pytest

from pytentacle import AsyncOctopusClient, OctopusClient


@pytest.fixture
def api_key() -> str:
    """Return a test API key."""
    return "sk_test_1234567890"


@pytest.fixture
def client(api_key: str) -> OctopusClient:
    """Return a test client."""
    return OctopusClient(api_key=api_key)


@pytest.fixture
async def async_client(api_key: str) -> AsyncOctopusClient:
    """Return an async test client."""
    return AsyncOctopusClient(api_key=api_key)
