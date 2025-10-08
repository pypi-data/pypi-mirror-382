"""Industry data API endpoints."""

from typing import TYPE_CHECKING

from pytentacle.models.common import GridSupplyPoint

if TYPE_CHECKING:
    from pytentacle.core.base import BaseClient


class IndustryAPI:
    """Industry data API endpoints.

    Provides access to Grid Supply Point (GSP) data.
    GSPs are the 14 regional distribution zones in the UK.
    """

    def __init__(self, client: "BaseClient") -> None:
        """Initialize the industry API.

        Args:
            client: The HTTP client to use
        """
        self.client = client

    def get_grid_supply_points(
        self,
        postcode: str | None = None,
    ) -> list[GridSupplyPoint]:
        """Get list of Grid Supply Points, optionally filtered by postcode.

        Args:
            postcode: Optional UK postcode to filter by

        Returns:
            List of GridSupplyPoint objects
        """
        params = {}
        if postcode:
            params["postcode"] = postcode

        results = self.client.get_paginated("industry/grid-supply-points/", params)
        return [GridSupplyPoint.model_validate(item) for item in results]
