"""Tests for Industry API endpoints."""

from unittest.mock import MagicMock

import pytest

from pytentacle.api.industry import IndustryAPI
from pytentacle.models.common import GridSupplyPoint


@pytest.fixture
def industry_api() -> IndustryAPI:
    """Return an industry API instance with mocked client."""
    client = MagicMock()
    return IndustryAPI(client)


@pytest.fixture
def mock_gsp_data() -> dict:
    """Return mock Grid Supply Point data."""
    return {
        "groupId": "_A",
    }


class TestGetGridSupplyPoints:
    """Tests for get_grid_supply_points method."""

    def test_get_grid_supply_points_no_filter(
        self, industry_api: IndustryAPI, mock_gsp_data: dict
    ) -> None:
        """Test getting all grid supply points without filter."""
        industry_api.client.get_paginated.return_value = [mock_gsp_data]  # type: ignore[attr-defined]

        result = industry_api.get_grid_supply_points()

        industry_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "industry/grid-supply-points/", {}
        )
        assert len(result) == 1
        assert isinstance(result[0], GridSupplyPoint)
        assert result[0].group_id == "_A"

    def test_get_grid_supply_points_with_postcode(
        self, industry_api: IndustryAPI, mock_gsp_data: dict
    ) -> None:
        """Test getting grid supply points filtered by postcode."""
        industry_api.client.get_paginated.return_value = [mock_gsp_data]  # type: ignore[attr-defined]

        result = industry_api.get_grid_supply_points(postcode="SW1A 1AA")

        industry_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "industry/grid-supply-points/", {"postcode": "SW1A 1AA"}
        )
        assert len(result) == 1
        assert isinstance(result[0], GridSupplyPoint)
