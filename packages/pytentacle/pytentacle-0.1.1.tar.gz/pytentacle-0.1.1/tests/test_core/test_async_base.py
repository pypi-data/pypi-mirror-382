"""Tests for AsyncBaseClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from pytentacle.core.async_base import AsyncBaseClient
from pytentacle.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


@pytest.fixture
def async_base_client() -> AsyncBaseClient:
    """Return an async base client instance."""
    return AsyncBaseClient(api_key="test_key")


@pytest.fixture
def mock_response() -> MagicMock:
    """Return a mock HTTP response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"test": "data"}
    return response


class TestAsyncBaseClientInit:
    """Tests for AsyncBaseClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with API key."""
        client = AsyncBaseClient(api_key="test_key")
        assert client.base_url == "https://api.octopus.energy/v1"
        assert client.timeout == 30.0
        assert client.auth is not None

    def test_init_without_api_key(self) -> None:
        """Test initialization without API key."""
        client = AsyncBaseClient()
        assert client.auth is None

    def test_init_with_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = AsyncBaseClient(base_url="https://custom.url")
        assert client.base_url == "https://custom.url"

    def test_init_with_custom_timeout(self) -> None:
        """Test initialization with custom timeout."""
        client = AsyncBaseClient(timeout=60.0)
        assert client.timeout == 60.0


class TestAsyncBaseClientProperty:
    """Tests for AsyncBaseClient client property."""

    def test_client_property_creates_client(
        self, async_base_client: AsyncBaseClient
    ) -> None:
        """Test that client property creates httpx.AsyncClient."""
        client = async_base_client.client
        assert isinstance(client, httpx.AsyncClient)

    def test_client_property_reuses_client(
        self, async_base_client: AsyncBaseClient
    ) -> None:
        """Test that client property reuses the same client instance."""
        client1 = async_base_client.client
        client2 = async_base_client.client
        assert client1 is client2


class TestAsyncGetHeaders:
    """Tests for _get_headers method."""

    def test_get_headers_with_auth(self, async_base_client: AsyncBaseClient) -> None:
        """Test getting headers with authentication."""
        headers = async_base_client._get_headers()
        assert "Content-Type" in headers
        assert "Authorization" in headers

    def test_get_headers_without_auth(self) -> None:
        """Test getting headers without authentication."""
        client = AsyncBaseClient()
        headers = client._get_headers()
        assert "Content-Type" in headers
        assert "Authorization" not in headers


class TestAsyncHandleResponse:
    """Tests for _handle_response method."""

    def test_handle_response_success(
        self, async_base_client: AsyncBaseClient, mock_response: MagicMock
    ) -> None:
        """Test handling successful response."""
        result = async_base_client._handle_response(mock_response)
        assert result == {"test": "data"}

    def test_handle_response_401(self, async_base_client: AsyncBaseClient) -> None:
        """Test handling 401 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 401

        with pytest.raises(AuthenticationError) as exc_info:
            async_base_client._handle_response(response)
        assert exc_info.value.status_code == 401

    def test_handle_response_404(self, async_base_client: AsyncBaseClient) -> None:
        """Test handling 404 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 404

        with pytest.raises(NotFoundError) as exc_info:
            async_base_client._handle_response(response)
        assert exc_info.value.status_code == 404

    def test_handle_response_400(self, async_base_client: AsyncBaseClient) -> None:
        """Test handling 400 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 400
        response.json.return_value = {"detail": "Invalid request"}

        with pytest.raises(ValidationError) as exc_info:
            async_base_client._handle_response(response)
        assert exc_info.value.status_code == 400

    def test_handle_response_400_no_detail(
        self, async_base_client: AsyncBaseClient
    ) -> None:
        """Test handling 400 response without detail."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 400
        response.json.side_effect = Exception("No JSON")

        with pytest.raises(ValidationError) as exc_info:
            async_base_client._handle_response(response)
        assert "Validation error" in str(exc_info.value)

    def test_handle_response_429(self, async_base_client: AsyncBaseClient) -> None:
        """Test handling 429 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 429

        with pytest.raises(RateLimitError) as exc_info:
            async_base_client._handle_response(response)
        assert exc_info.value.status_code == 429

    def test_handle_response_500(self, async_base_client: AsyncBaseClient) -> None:
        """Test handling 500 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 500

        with pytest.raises(ServerError) as exc_info:
            async_base_client._handle_response(response)
        assert exc_info.value.status_code == 500

    def test_handle_response_503(self, async_base_client: AsyncBaseClient) -> None:
        """Test handling 503 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 503

        with pytest.raises(ServerError) as exc_info:
            async_base_client._handle_response(response)
        assert exc_info.value.status_code == 503


class TestAsyncGet:
    """Tests for get method."""

    @pytest.mark.asyncio
    async def test_get_success(self, async_base_client: AsyncBaseClient) -> None:
        """Test successful GET request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        async_base_client._client = mock_client

        result = await async_base_client.get("test-endpoint")

        assert result == {"data": "test"}
        mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_with_params(self, async_base_client: AsyncBaseClient) -> None:
        """Test GET request with parameters."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        async_base_client._client = mock_client

        result = await async_base_client.get("test-endpoint", {"param": "value"})

        assert result == {"data": "test"}
        call_args = mock_client.get.call_args
        assert call_args.kwargs["params"] == {"param": "value"}


class TestAsyncGetPaginated:
    """Tests for get_paginated method."""

    @pytest.mark.asyncio
    async def test_get_paginated_single_page(
        self, async_base_client: AsyncBaseClient
    ) -> None:
        """Test paginated GET with single page."""
        mock_response = {
            "results": [{"id": 1}, {"id": 2}],
            "next": None,
        }

        with patch.object(async_base_client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await async_base_client.get_paginated("test-endpoint")

            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 2

    @pytest.mark.asyncio
    async def test_get_paginated_multiple_pages(
        self, async_base_client: AsyncBaseClient
    ) -> None:
        """Test paginated GET with multiple pages."""
        page1 = {
            "results": [{"id": 1}],
            "next": "https://api.test.com/endpoint?page=2",
        }
        page2 = {
            "results": [{"id": 2}],
            "next": None,
        }

        with patch.object(async_base_client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [page1, page2]

            result = await async_base_client.get_paginated("test-endpoint")

            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 2

    @pytest.mark.asyncio
    async def test_get_paginated_non_paginated_response(
        self, async_base_client: AsyncBaseClient
    ) -> None:
        """Test paginated GET with non-paginated response."""
        mock_response = {"id": 1, "name": "test"}

        with patch.object(async_base_client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await async_base_client.get_paginated("test-endpoint")

            assert len(result) == 1
            assert result[0] == mock_response


class TestAsyncClose:
    """Tests for close method."""

    @pytest.mark.asyncio
    async def test_close(self, async_base_client: AsyncBaseClient) -> None:
        """Test closing the client."""
        # Create the client first
        _ = async_base_client.client

        await async_base_client.close()
        assert async_base_client._client is None


class TestAsyncContextManager:
    """Tests for async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test using client as async context manager."""
        async with AsyncBaseClient(api_key="test_key") as client:
            assert client is not None
            assert isinstance(client, AsyncBaseClient)
