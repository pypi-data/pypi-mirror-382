"""Tests for exceptions."""

from pytentacle.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PytentacleError,
    RateLimitError,
    ServerError,
    ValidationError,
)


def test_base_exception() -> None:
    """Test base PytentacleError."""
    error = PytentacleError("Test error")
    assert str(error) == "Test error"


def test_api_error() -> None:
    """Test APIError with status code."""
    error = APIError("API error", status_code=400)
    assert str(error) == "API error"
    assert error.status_code == 400


def test_authentication_error() -> None:
    """Test AuthenticationError."""
    error = AuthenticationError("Auth failed", status_code=401)
    assert str(error) == "Auth failed"
    assert error.status_code == 401
    assert isinstance(error, APIError)


def test_validation_error() -> None:
    """Test ValidationError."""
    error = ValidationError("Validation failed", status_code=400)
    assert isinstance(error, APIError)


def test_not_found_error() -> None:
    """Test NotFoundError."""
    error = NotFoundError("Not found", status_code=404)
    assert isinstance(error, APIError)


def test_rate_limit_error() -> None:
    """Test RateLimitError."""
    error = RateLimitError("Rate limited", status_code=429)
    assert isinstance(error, APIError)


def test_server_error() -> None:
    """Test ServerError."""
    error = ServerError("Server error", status_code=500)
    assert isinstance(error, APIError)
