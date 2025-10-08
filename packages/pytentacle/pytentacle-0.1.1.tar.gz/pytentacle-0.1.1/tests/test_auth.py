"""Tests for authentication."""

from pytentacle.auth import APIKeyAuth


def test_api_key_auth() -> None:
    """Test API key authentication."""
    auth = APIKeyAuth("test_key_12345")
    headers = auth.get_headers()

    assert "Authorization" in headers
    assert headers["Authorization"] == "Basic dGVzdF9rZXlfMTIzNDU6"


def test_api_key_auth_repr() -> None:
    """Test API key auth string representation."""
    auth = APIKeyAuth("test_key_12345")
    repr_str = repr(auth)

    assert "***2345" in repr_str
    assert "test_key" not in repr_str  # Full key should be hidden
