"""Asynchronous Octopus Energy API client."""

import os

from dotenv import load_dotenv

from pytentacle.api.electricity import ElectricityAPI
from pytentacle.api.gas import GasAPI
from pytentacle.api.industry import IndustryAPI
from pytentacle.api.products import ProductsAPI
from pytentacle.core.async_base import AsyncBaseClient

# Load environment variables from .env file
load_dotenv()


class AsyncOctopusClient:
    """Asynchronous client for the Octopus Energy API.

    This client provides async access to all public Octopus Energy API endpoints.
    Most endpoints require authentication with an API key.

    Example:
        ```python
        from pytentacle import AsyncOctopusClient

        async with AsyncOctopusClient(api_key="sk_live_...") as client:
            # List all products
            products = await client.products.list()

            # Get specific product
            product = await client.products.get("AGILE-24-04-03")

            # Get consumption data
            consumption = await client.electricity.get_consumption(
                mpan="1234567890123",
                serial_number="12A3456789",
            )
        ```
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the async Octopus Energy API client.

        Args:
            api_key: API key for authentication. If not provided, will attempt to
                read from OCTOPUS_API_KEY environment variable or .env file.
            base_url: Optional base URL (defaults to production API)
            timeout: Request timeout in seconds (default: 30.0)
        """
        # Use provided API key or fall back to environment variable
        if api_key is None:
            api_key = os.getenv("OCTOPUS_API_KEY")

        self._base_client = AsyncBaseClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

        # Initialize API modules
        # Note: These modules will need to be made async-aware
        # For now, we'll reuse the sync API modules with the async base client
        self.products = ProductsAPI(self._base_client)  # type: ignore[arg-type]
        self.electricity = ElectricityAPI(self._base_client)  # type: ignore[arg-type]
        self.gas = GasAPI(self._base_client)  # type: ignore[arg-type]
        self.industry = IndustryAPI(self._base_client)  # type: ignore[arg-type]

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._base_client.close()

    async def __aenter__(self) -> "AsyncOctopusClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        """Return string representation."""
        auth_status = "authenticated" if self._base_client.auth else "unauthenticated"
        return f"AsyncOctopusClient({auth_status})"
