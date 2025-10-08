"""Exceptions for the Pytentacle library."""


class PytentacleError(Exception):
    """Base exception for all Pytentacle errors."""


class APIError(PytentacleError):
    """Raised when the API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize the APIError.

        Args:
            message: Error message from the API
            status_code: HTTP status code
        """
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Raised when authentication fails."""


class ValidationError(APIError):
    """Raised when request validation fails."""


class NotFoundError(APIError):
    """Raised when a resource is not found."""


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""


class ServerError(APIError):
    """Raised when the server returns a 5xx error."""
