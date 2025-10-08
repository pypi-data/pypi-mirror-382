"""Tests for the main client."""

from unittest.mock import patch

from pytentacle import OctopusClient


def test_client_initialization() -> None:
    """Test OctopusClient initialization."""
    client = OctopusClient(api_key="test_key")

    assert client.products is not None
    assert client.electricity is not None
    assert client.gas is not None
    assert client.industry is not None


def test_client_context_manager() -> None:
    """Test OctopusClient as context manager."""
    with OctopusClient(api_key="test_key") as client:
        assert client.products is not None

    assert client._base_client._client is None  # Should be closed


@patch.dict("os.environ", {}, clear=True)
def test_client_repr() -> None:
    """Test OctopusClient string representation."""
    client = OctopusClient(api_key="test_key")
    assert "authenticated" in repr(client)

    client_no_auth = OctopusClient()
    assert "unauthenticated" in repr(client_no_auth)
