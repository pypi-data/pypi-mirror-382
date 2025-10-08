"""Authentication for the Octopus Energy API."""

import base64

from pytentacle.types import Headers


class APIKeyAuth:
    """API Key authentication for Octopus Energy API.

    The API uses Basic Authentication with the API key as username and empty password.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize API key authentication.

        Args:
            api_key: The API key from Octopus Energy
        """
        self.api_key = api_key

    def get_headers(self) -> Headers:
        """Get authentication headers.

        Returns:
            Dictionary containing the Authorization header
        """
        credentials = f"{self.api_key}:"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def __repr__(self) -> str:
        """Return string representation."""
        return f"APIKeyAuth(api_key='***{self.api_key[-4:]}')"
