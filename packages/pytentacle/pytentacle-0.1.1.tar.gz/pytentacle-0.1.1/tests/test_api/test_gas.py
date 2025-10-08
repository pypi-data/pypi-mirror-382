"""Tests for Gas API endpoints."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from pytentacle.api.gas import GasAPI
from pytentacle.models.consumption import Consumption


@pytest.fixture
def gas_api() -> GasAPI:
    """Return a gas API instance with mocked client."""
    client = MagicMock()
    return GasAPI(client)


@pytest.fixture
def mock_consumption_data() -> dict:
    """Return mock consumption data."""
    return {
        "consumption": 10.5,
        "interval_start": "2024-01-01T00:00:00Z",
        "interval_end": "2024-01-01T00:30:00Z",
    }


class TestGetConsumption:
    """Tests for get_consumption method."""

    def test_get_consumption_minimal(
        self, gas_api: GasAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with minimal parameters."""
        gas_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]

        result = gas_api.get_consumption("1234567890", "G12A3456789")

        expected_endpoint = (
            "gas-meter-points/1234567890/meters/G12A3456789/consumption/"
        )
        gas_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint, {"order_by": "-period"}
        )
        assert len(result) == 1
        assert isinstance(result[0], Consumption)
        assert result[0].consumption == 10.5

    def test_get_consumption_with_dates(
        self, gas_api: GasAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with date filters."""
        gas_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]
        period_from = datetime(2024, 1, 1, tzinfo=timezone.utc)
        period_to = datetime(2024, 1, 31, tzinfo=timezone.utc)

        result = gas_api.get_consumption(
            "1234567890",
            "G12A3456789",
            period_from=period_from,
            period_to=period_to,
        )

        expected_endpoint = (
            "gas-meter-points/1234567890/meters/G12A3456789/consumption/"
        )
        gas_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "order_by": "-period",
                "period_from": "2024-01-01T00:00:00+00:00",
                "period_to": "2024-01-31T00:00:00+00:00",
            },
        )
        assert len(result) == 1

    def test_get_consumption_with_page_size(
        self, gas_api: GasAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with page size."""
        gas_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]

        result = gas_api.get_consumption(
            "1234567890",
            "G12A3456789",
            page_size=5000,
        )

        expected_endpoint = (
            "gas-meter-points/1234567890/meters/G12A3456789/consumption/"
        )
        gas_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "order_by": "-period",
                "page_size": 5000,
            },
        )
        assert len(result) == 1

    def test_get_consumption_with_order_by_asc(
        self, gas_api: GasAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with ascending order."""
        gas_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]

        result = gas_api.get_consumption(
            "1234567890",
            "G12A3456789",
            order_by="period",
        )

        expected_endpoint = (
            "gas-meter-points/1234567890/meters/G12A3456789/consumption/"
        )
        gas_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "order_by": "period",
            },
        )
        assert len(result) == 1

    def test_get_consumption_with_group_by(
        self, gas_api: GasAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption grouped by day."""
        gas_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]

        result = gas_api.get_consumption(
            "1234567890",
            "G12A3456789",
            group_by="day",
        )

        expected_endpoint = (
            "gas-meter-points/1234567890/meters/G12A3456789/consumption/"
        )
        gas_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "order_by": "-period",
                "group_by": "day",
            },
        )
        assert len(result) == 1

    def test_get_consumption_with_all_params(
        self, gas_api: GasAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with all parameters."""
        gas_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]
        period_from = datetime(2024, 1, 1, tzinfo=timezone.utc)
        period_to = datetime(2024, 1, 31, tzinfo=timezone.utc)

        result = gas_api.get_consumption(
            "1234567890",
            "G12A3456789",
            period_from=period_from,
            period_to=period_to,
            page_size=10000,
            order_by="period",
            group_by="week",
        )

        expected_endpoint = (
            "gas-meter-points/1234567890/meters/G12A3456789/consumption/"
        )
        gas_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "order_by": "period",
                "period_from": "2024-01-01T00:00:00+00:00",
                "period_to": "2024-01-31T00:00:00+00:00",
                "page_size": 10000,
                "group_by": "week",
            },
        )
        assert len(result) == 1
