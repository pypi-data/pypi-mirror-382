"""Tests for Electricity API endpoints."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from pytentacle.api.electricity import ElectricityAPI
from pytentacle.models.consumption import Consumption
from pytentacle.models.meter_points import ElectricityMeterPoint


@pytest.fixture
def electricity_api() -> ElectricityAPI:
    """Return an electricity API instance with mocked client."""
    client = MagicMock()
    return ElectricityAPI(client)


@pytest.fixture
def mock_meter_point_data() -> dict:
    """Return mock electricity meter point data."""
    return {
        "mpan": "1234567890123",
        "profile_class": 1,
        "consumption_standard": 2900,
        "gsp": "_A",
    }


@pytest.fixture
def mock_consumption_data() -> dict:
    """Return mock consumption data."""
    return {
        "consumption": 0.5,
        "interval_start": "2024-01-01T00:00:00Z",
        "interval_end": "2024-01-01T00:30:00Z",
    }


class TestGetMeterPoint:
    """Tests for get_meter_point method."""

    def test_get_meter_point(
        self, electricity_api: ElectricityAPI, mock_meter_point_data: dict
    ) -> None:
        """Test getting an electricity meter point."""
        electricity_api.client.get.return_value = mock_meter_point_data  # type: ignore[attr-defined]

        result = electricity_api.get_meter_point("1234567890123")

        electricity_api.client.get.assert_called_once_with(
            "electricity-meter-points/1234567890123/"
        )  # type: ignore[attr-defined]
        assert isinstance(result, ElectricityMeterPoint)
        assert result.mpan == "1234567890123"


class TestGetConsumption:
    """Tests for get_consumption method."""

    def test_get_consumption_minimal(
        self, electricity_api: ElectricityAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with minimal parameters."""
        electricity_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]

        result = electricity_api.get_consumption("1234567890123", "12A3456789")

        expected_endpoint = (
            "electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        )
        electricity_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint, {"order_by": "-period"}
        )
        assert len(result) == 1
        assert isinstance(result[0], Consumption)
        assert result[0].consumption == 0.5

    def test_get_consumption_with_dates(
        self, electricity_api: ElectricityAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with date filters."""
        electricity_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]
        period_from = datetime(2024, 1, 1, tzinfo=timezone.utc)
        period_to = datetime(2024, 1, 31, tzinfo=timezone.utc)

        result = electricity_api.get_consumption(
            "1234567890123",
            "12A3456789",
            period_from=period_from,
            period_to=period_to,
        )

        expected_endpoint = (
            "electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        )
        electricity_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "order_by": "-period",
                "period_from": "2024-01-01T00:00:00+00:00",
                "period_to": "2024-01-31T00:00:00+00:00",
            },
        )
        assert len(result) == 1

    def test_get_consumption_with_page_size(
        self, electricity_api: ElectricityAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with page size."""
        electricity_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]

        result = electricity_api.get_consumption(
            "1234567890123",
            "12A3456789",
            page_size=5000,
        )

        expected_endpoint = (
            "electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        )
        electricity_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "order_by": "-period",
                "page_size": 5000,
            },
        )
        assert len(result) == 1

    def test_get_consumption_with_order_by_asc(
        self, electricity_api: ElectricityAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with ascending order."""
        electricity_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]

        result = electricity_api.get_consumption(
            "1234567890123",
            "12A3456789",
            order_by="period",
        )

        expected_endpoint = (
            "electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        )
        electricity_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "order_by": "period",
            },
        )
        assert len(result) == 1

    def test_get_consumption_with_group_by(
        self, electricity_api: ElectricityAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption grouped by day."""
        electricity_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]

        result = electricity_api.get_consumption(
            "1234567890123",
            "12A3456789",
            group_by="day",
        )

        expected_endpoint = (
            "electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        )
        electricity_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "order_by": "-period",
                "group_by": "day",
            },
        )
        assert len(result) == 1

    def test_get_consumption_with_all_params(
        self, electricity_api: ElectricityAPI, mock_consumption_data: dict
    ) -> None:
        """Test getting consumption with all parameters."""
        electricity_api.client.get_paginated.return_value = [mock_consumption_data]  # type: ignore[attr-defined]
        period_from = datetime(2024, 1, 1, tzinfo=timezone.utc)
        period_to = datetime(2024, 1, 31, tzinfo=timezone.utc)

        result = electricity_api.get_consumption(
            "1234567890123",
            "12A3456789",
            period_from=period_from,
            period_to=period_to,
            page_size=10000,
            order_by="period",
            group_by="week",
        )

        expected_endpoint = (
            "electricity-meter-points/1234567890123/meters/12A3456789/consumption/"
        )
        electricity_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
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
