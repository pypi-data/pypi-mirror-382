"""Tests for AsyncOctopusClient."""

from unittest.mock import patch

import pytest

from pytentacle import AsyncOctopusClient
from pytentacle.api.electricity import ElectricityAPI
from pytentacle.api.gas import GasAPI
from pytentacle.api.industry import IndustryAPI
from pytentacle.api.products import ProductsAPI
from pytentacle.core.async_base import AsyncBaseClient


class TestAsyncOctopusClientInit:
    """Tests for AsyncOctopusClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with API key."""
        client = AsyncOctopusClient(api_key="test_key")

        assert client._base_client.auth is not None
        assert client._base_client.auth.api_key == "test_key"
        assert isinstance(client._base_client, AsyncBaseClient)

    @patch.dict("os.environ", {}, clear=True)
    def test_init_without_api_key(self) -> None:
        """Test initialization without API key."""
        client = AsyncOctopusClient()

        assert client._base_client.auth is None

    def test_init_with_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = AsyncOctopusClient(base_url="https://custom.url")

        assert client._base_client.base_url == "https://custom.url"

    def test_init_with_custom_timeout(self) -> None:
        """Test initialization with custom timeout."""
        client = AsyncOctopusClient(timeout=60.0)

        assert client._base_client.timeout == 60.0

    def test_api_modules_initialized(self) -> None:
        """Test that all API modules are initialized."""
        client = AsyncOctopusClient(api_key="test_key")

        assert isinstance(client.products, ProductsAPI)
        assert isinstance(client.electricity, ElectricityAPI)
        assert isinstance(client.gas, GasAPI)
        assert isinstance(client.industry, IndustryAPI)


class TestAsyncOctopusClientMethods:
    """Tests for AsyncOctopusClient methods."""

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        """Test closing the client."""
        client = AsyncOctopusClient(api_key="test_key")

        # Trigger client creation
        _ = client._base_client.client

        await client.close()
        assert client._base_client._client is None

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test using client as async context manager."""
        async with AsyncOctopusClient(api_key="test_key") as client:
            assert client is not None
            assert isinstance(client, AsyncOctopusClient)

    def test_repr_authenticated(self) -> None:
        """Test string representation with authentication."""
        client = AsyncOctopusClient(api_key="test_key")

        assert repr(client) == "AsyncOctopusClient(authenticated)"

    @patch.dict("os.environ", {}, clear=True)
    def test_repr_unauthenticated(self) -> None:
        """Test string representation without authentication."""
        client = AsyncOctopusClient()

        assert repr(client) == "AsyncOctopusClient(unauthenticated)"
