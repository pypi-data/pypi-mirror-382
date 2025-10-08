"""Gas meter points API endpoints."""

import os
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pytentacle.models.consumption import Consumption

if TYPE_CHECKING:
    from pytentacle.core.base import BaseClient


class GasAPI:
    """Gas meter points API endpoints.

    Provides access to gas consumption data.
    Note: Half-hourly consumption data is only available for smart meters.
    Gas consumption units vary: kWh for SMETS1, m³ for SMETS2.
    """

    def __init__(self, client: "BaseClient") -> None:
        """Initialize the gas API.

        Args:
            client: The HTTP client to use
        """
        self.client = client

    def get_consumption(  # noqa: PLR0913
        self,
        mprn: str | None = None,
        serial_number: str | None = None,
        *,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        page_size: int | None = None,
        order_by: Literal["period", "-period"] = "-period",
        group_by: Literal["hour", "day", "week", "month", "quarter"] | None = None,
    ) -> list[Consumption]:
        """Get gas consumption data for a meter.

        Half-hourly consumption data is only available for smart meters.
        Non-smart meter requests will return empty results.
        Units vary: kWh for SMETS1, m³ for SMETS2.

        Args:
            mprn: Meter Point Reference Number. If not provided,
                will attempt to read from OCTOPUS_GAS_MPRN environment variable.
            serial_number: Gas meter serial number. If not provided,
                will attempt to read from OCTOPUS_GAS_SERIAL_NUMBER
                environment variable.
            period_from: Filter consumption from this datetime (inclusive)
            period_to: Filter consumption to this datetime (exclusive)
            page_size: Number of results per page (max 25000)
            order_by: Sort order - 'period' (ascending) or '-period' (descending)
            group_by: Group results by time period

        Returns:
            List of Consumption objects

        Raises:
            ValueError: If mprn or serial_number is not provided and not found
                in environment
        """
        if mprn is None:
            mprn = os.getenv("OCTOPUS_GAS_MPRN")
            if mprn is None:
                msg = (
                    "mprn is required. Provide it as an argument or set "
                    "OCTOPUS_GAS_MPRN environment variable."
                )
                raise ValueError(msg)

        if serial_number is None:
            serial_number = os.getenv("OCTOPUS_GAS_SERIAL_NUMBER")
            if serial_number is None:
                msg = (
                    "serial_number is required. Provide it as an argument or "
                    "set OCTOPUS_GAS_SERIAL_NUMBER environment variable."
                )
                raise ValueError(msg)
        params: dict[str, str | int] = {"order_by": order_by}
        if period_from:
            params["period_from"] = period_from.isoformat()
        if period_to:
            params["period_to"] = period_to.isoformat()
        if page_size:
            params["page_size"] = page_size
        if group_by:
            params["group_by"] = group_by

        endpoint = f"gas-meter-points/{mprn}/meters/{serial_number}/consumption/"
        results = self.client.get_paginated(endpoint, params)
        return [Consumption.model_validate(item) for item in results]
