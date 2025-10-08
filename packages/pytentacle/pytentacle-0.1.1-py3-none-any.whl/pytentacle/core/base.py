"""Base HTTP client for synchronous requests."""

from typing import Any

import httpx

from pytentacle.auth import APIKeyAuth
from pytentacle.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from pytentacle.types import Headers, JSONDict


class BaseClient:
    """Base HTTP client for the Octopus Energy API."""

    BASE_URL = "https://api.octopus.energy/v1"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the base client.

        Args:
            api_key: Optional API key for authentication
            base_url: Optional base URL (defaults to production API)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.auth = APIKeyAuth(api_key) if api_key else None
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Get or create the HTTP client.

        Returns:
            httpx.Client instance
        """
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def _get_headers(self) -> Headers:
        """Get request headers including authentication.

        Returns:
            Dictionary of headers
        """
        headers: Headers = {"Content-Type": "application/json"}
        if self.auth:
            headers.update(self.auth.get_headers())
        return headers

    def _handle_response(self, response: httpx.Response) -> JSONDict:
        """Handle API response and raise appropriate exceptions.

        Args:
            response: The HTTP response

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: For 401 responses
            NotFoundError: For 404 responses
            ValidationError: For 400 responses
            RateLimitError: For 429 responses
            ServerError: For 5xx responses
        """
        if response.status_code == 401:
            msg = "Authentication failed. Check your API key."
            raise AuthenticationError(
                msg,
                status_code=401,
            )
        if response.status_code == 404:
            msg = "Resource not found."
            raise NotFoundError(
                msg,
                status_code=404,
            )
        if response.status_code == 400:
            try:
                error_data = response.json()
                message = error_data.get("detail", "Validation error")
            except Exception:  # noqa: BLE001
                message = "Validation error"
            raise ValidationError(message, status_code=400)
        if response.status_code == 429:
            msg = "Rate limit exceeded. Please try again later."
            raise RateLimitError(
                msg,
                status_code=429,
            )
        if response.status_code >= 500:
            msg = f"Server error: {response.status_code}"
            raise ServerError(
                msg,
                status_code=response.status_code,
            )

        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> JSONDict:
        """Make a GET request.

        Args:
            endpoint: API endpoint (relative to base URL)
            params: Optional query parameters

        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.client.get(url, params=params, headers=self._get_headers())
        return self._handle_response(response)

    def get_paginated(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> list[JSONDict]:
        """Make a GET request and handle pagination automatically.

        Args:
            endpoint: API endpoint (relative to base URL)
            params: Optional query parameters

        Returns:
            List of all results from all pages
        """
        all_results: list[JSONDict] = []
        current_params = params.copy() if params else {}

        while True:
            data = self.get(endpoint, current_params)

            # Check if response has pagination structure
            if isinstance(data, dict) and "results" in data:
                all_results.extend(data["results"])

                # Check for next page
                if data.get("next"):
                    # Extract page number from next URL
                    next_url = data["next"]
                    if "page=" in next_url:
                        page_num = next_url.split("page=")[1].split("&")[0]
                        current_params["page"] = page_num
                    else:
                        break
                else:
                    break
            else:
                # Not a paginated response, return as-is
                return [data]

        return all_results

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "BaseClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit."""
        self.close()
