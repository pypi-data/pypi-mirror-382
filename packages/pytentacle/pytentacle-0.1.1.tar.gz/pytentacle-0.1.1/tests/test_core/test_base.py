"""Tests for base HTTP client."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from pytentacle.core.base import BaseClient
from pytentacle.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


@pytest.fixture
def base_client() -> BaseClient:
    """Return a base client instance."""
    return BaseClient(api_key="test_key")


@pytest.fixture
def mock_response() -> MagicMock:
    """Return a mock HTTP response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"test": "data"}
    return response


class TestBaseClientInit:
    """Tests for BaseClient initialization."""

    def test_base_client_initialization(self) -> None:
        """Test BaseClient initialization."""
        client = BaseClient(api_key="test_key")

        assert client.auth is not None
        assert client.auth.api_key == "test_key"
        assert client.base_url == "https://api.octopus.energy/v1"
        assert client.timeout == 30.0

    def test_base_client_without_auth(self) -> None:
        """Test BaseClient without authentication."""
        client = BaseClient()

        assert client.auth is None
        assert client.base_url == "https://api.octopus.energy/v1"

    def test_base_client_custom_base_url(self) -> None:
        """Test BaseClient with custom base URL."""
        custom_url = "https://custom.api.example.com/v1"
        client = BaseClient(base_url=custom_url)

        assert client.base_url == custom_url

    def test_init_with_custom_timeout(self) -> None:
        """Test initialization with custom timeout."""
        client = BaseClient(timeout=60.0)
        assert client.timeout == 60.0


class TestBaseClientProperty:
    """Tests for BaseClient client property."""

    def test_client_property_creates_client(self, base_client: BaseClient) -> None:
        """Test that client property creates httpx.Client."""
        client = base_client.client
        assert isinstance(client, httpx.Client)

    def test_client_property_reuses_client(self, base_client: BaseClient) -> None:
        """Test that client property reuses the same client instance."""
        client1 = base_client.client
        client2 = base_client.client
        assert client1 is client2


class TestGetHeaders:
    """Tests for _get_headers method."""

    def test_get_headers_with_auth(self, base_client: BaseClient) -> None:
        """Test getting headers with authentication."""
        headers = base_client._get_headers()
        assert "Content-Type" in headers
        assert "Authorization" in headers

    def test_get_headers_without_auth(self) -> None:
        """Test getting headers without authentication."""
        client = BaseClient()
        headers = client._get_headers()
        assert "Content-Type" in headers
        assert "Authorization" not in headers


class TestHandleResponse:
    """Tests for _handle_response method."""

    def test_handle_response_success(
        self, base_client: BaseClient, mock_response: MagicMock
    ) -> None:
        """Test handling successful response."""
        result = base_client._handle_response(mock_response)
        assert result == {"test": "data"}

    def test_handle_response_401(self, base_client: BaseClient) -> None:
        """Test handling 401 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 401

        with pytest.raises(AuthenticationError) as exc_info:
            base_client._handle_response(response)
        assert exc_info.value.status_code == 401

    def test_handle_response_404(self, base_client: BaseClient) -> None:
        """Test handling 404 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 404

        with pytest.raises(NotFoundError) as exc_info:
            base_client._handle_response(response)
        assert exc_info.value.status_code == 404

    def test_handle_response_400(self, base_client: BaseClient) -> None:
        """Test handling 400 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 400
        response.json.return_value = {"detail": "Invalid request"}

        with pytest.raises(ValidationError) as exc_info:
            base_client._handle_response(response)
        assert exc_info.value.status_code == 400

    def test_handle_response_400_no_detail(self, base_client: BaseClient) -> None:
        """Test handling 400 response without detail."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 400
        response.json.side_effect = Exception("No JSON")

        with pytest.raises(ValidationError) as exc_info:
            base_client._handle_response(response)
        assert "Validation error" in str(exc_info.value)

    def test_handle_response_429(self, base_client: BaseClient) -> None:
        """Test handling 429 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 429

        with pytest.raises(RateLimitError) as exc_info:
            base_client._handle_response(response)
        assert exc_info.value.status_code == 429

    def test_handle_response_500(self, base_client: BaseClient) -> None:
        """Test handling 500 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 500

        with pytest.raises(ServerError) as exc_info:
            base_client._handle_response(response)
        assert exc_info.value.status_code == 500

    def test_handle_response_503(self, base_client: BaseClient) -> None:
        """Test handling 503 response."""
        response = MagicMock(spec=httpx.Response)
        response.status_code = 503

        with pytest.raises(ServerError) as exc_info:
            base_client._handle_response(response)
        assert exc_info.value.status_code == 503


class TestGet:
    """Tests for get method."""

    def test_get_success(self, base_client: BaseClient) -> None:
        """Test successful GET request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        with patch.object(base_client.client, "get", return_value=mock_response):
            result = base_client.get("test-endpoint")

            assert result == {"data": "test"}

    def test_get_with_params(self, base_client: BaseClient) -> None:
        """Test GET request with parameters."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        with patch.object(
            base_client.client, "get", return_value=mock_response
        ) as mock_get:
            result = base_client.get("test-endpoint", {"param": "value"})

            assert result == {"data": "test"}
            call_args = mock_get.call_args
            assert call_args.kwargs["params"] == {"param": "value"}


class TestGetPaginated:
    """Tests for get_paginated method."""

    def test_get_paginated_single_page(self, base_client: BaseClient) -> None:
        """Test paginated GET with single page."""
        mock_response = {
            "results": [{"id": 1}, {"id": 2}],
            "next": None,
        }

        with patch.object(base_client, "get", return_value=mock_response):
            result = base_client.get_paginated("test-endpoint")

            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 2

    def test_get_paginated_multiple_pages(self, base_client: BaseClient) -> None:
        """Test paginated GET with multiple pages."""
        page1 = {
            "results": [{"id": 1}],
            "next": "https://api.test.com/endpoint?page=2",
        }
        page2 = {
            "results": [{"id": 2}],
            "next": None,
        }

        with patch.object(base_client, "get", side_effect=[page1, page2]):
            result = base_client.get_paginated("test-endpoint")

            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 2

    def test_get_paginated_non_paginated_response(
        self, base_client: BaseClient
    ) -> None:
        """Test paginated GET with non-paginated response."""
        mock_response = {"id": 1, "name": "test"}

        with patch.object(base_client, "get", return_value=mock_response):
            result = base_client.get_paginated("test-endpoint")

            assert len(result) == 1
            assert result[0] == mock_response


class TestClose:
    """Tests for close method."""

    def test_close(self, base_client: BaseClient) -> None:
        """Test closing the client."""
        # Create the client first
        _ = base_client.client

        base_client.close()
        assert base_client._client is None


class TestContextManager:
    """Tests for context manager."""

    def test_base_client_context_manager(self) -> None:
        """Test BaseClient as context manager."""
        with BaseClient(api_key="test_key") as client:
            assert client.auth is not None

        assert client._client is None  # Should be closed
