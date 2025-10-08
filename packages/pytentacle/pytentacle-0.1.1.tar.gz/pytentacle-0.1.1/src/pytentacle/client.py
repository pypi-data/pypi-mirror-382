"""Synchronous Octopus Energy API client."""

import os

from dotenv import load_dotenv

from pytentacle.api.electricity import ElectricityAPI
from pytentacle.api.gas import GasAPI
from pytentacle.api.industry import IndustryAPI
from pytentacle.api.products import ProductsAPI
from pytentacle.core.base import BaseClient

# Load environment variables from .env file
load_dotenv()


class OctopusClient:
    """Synchronous client for the Octopus Energy API.

    This client provides access to all public Octopus Energy API endpoints.
    Most endpoints require authentication with an API key.

    Example:
        ```python
        from pytentacle import OctopusClient

        client = OctopusClient(api_key="sk_live_...")

        # List all products
        products = client.products.list()

        # Get specific product
        product = client.products.get("AGILE-24-04-03")

        # Get consumption data
        consumption = client.electricity.get_consumption(
            mpan="1234567890123",
            serial_number="12A3456789",
        )

        # Remember to close the client
        client.close()
        ```

    Or use as a context manager:
        ```python
        with OctopusClient(api_key="sk_live_...") as client:
            products = client.products.list()
        ```
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the Octopus Energy API client.

        Args:
            api_key: API key for authentication. If not provided, will attempt to
                read from OCTOPUS_API_KEY environment variable or .env file.
            base_url: Optional base URL (defaults to production API)
            timeout: Request timeout in seconds (default: 30.0)
        """
        # Use provided API key or fall back to environment variable
        if api_key is None:
            api_key = os.getenv("OCTOPUS_API_KEY")

        self._base_client = BaseClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

        # Initialize API modules
        self.products = ProductsAPI(self._base_client)
        self.electricity = ElectricityAPI(self._base_client)
        self.gas = GasAPI(self._base_client)
        self.industry = IndustryAPI(self._base_client)

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._base_client.close()

    def __enter__(self) -> "OctopusClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """Return string representation."""
        auth_status = "authenticated" if self._base_client.auth else "unauthenticated"
        return f"OctopusClient({auth_status})"
