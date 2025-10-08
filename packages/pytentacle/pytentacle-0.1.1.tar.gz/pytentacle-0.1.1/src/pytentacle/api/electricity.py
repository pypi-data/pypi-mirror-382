"""Electricity meter points API endpoints."""

import os
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pytentacle.models.consumption import Consumption
from pytentacle.models.meter_points import ElectricityMeterPoint

if TYPE_CHECKING:
    from pytentacle.core.base import BaseClient


class ElectricityAPI:
    """Electricity meter points API endpoints.

    Provides access to electricity meter point details and consumption data.
    Note: Half-hourly consumption data is only available for smart meters.
    """

    def __init__(self, client: "BaseClient") -> None:
        """Initialize the electricity API.

        Args:
            client: The HTTP client to use
        """
        self.client = client

    def get_meter_point(self, mpan: str | None = None) -> ElectricityMeterPoint:
        """Get electricity meter point details.

        Args:
            mpan: Meter Point Administration Number (13 digits). If not provided,
                will attempt to read from OCTOPUS_ELECTRICITY_MPAN environment variable.

        Returns:
            ElectricityMeterPoint object

        Raises:
            ValueError: If mpan is not provided and not found in environment
        """
        if mpan is None:
            mpan = os.getenv("OCTOPUS_ELECTRICITY_MPAN")
            if mpan is None:
                msg = (
                    "mpan is required. Provide it as an argument or set "
                    "OCTOPUS_ELECTRICITY_MPAN environment variable."
                )
                raise ValueError(msg)

        data = self.client.get(f"electricity-meter-points/{mpan}/")
        return ElectricityMeterPoint.model_validate(data)

    def get_consumption(  # noqa: PLR0913
        self,
        mpan: str | None = None,
        serial_number: str | None = None,
        *,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        page_size: int | None = None,
        order_by: Literal["period", "-period"] = "-period",
        group_by: Literal["hour", "day", "week", "month", "quarter"] | None = None,
    ) -> list[Consumption]:
        """Get electricity consumption data for a meter.

        Half-hourly consumption data is only available for smart meters.
        Non-smart meter requests will return empty results.

        Args:
            mpan: Meter Point Administration Number (13 digits). If not provided,
                will attempt to read from OCTOPUS_ELECTRICITY_MPAN
                environment variable.
            serial_number: Electricity meter serial number. If not provided,
                will attempt to read from OCTOPUS_ELECTRICITY_SERIAL_NUMBER
                environment variable.
            period_from: Filter consumption from this datetime (inclusive)
            period_to: Filter consumption to this datetime (exclusive)
            page_size: Number of results per page (max 25000)
            order_by: Sort order - 'period' (ascending) or '-period' (descending)
            group_by: Group results by time period

        Returns:
            List of Consumption objects

        Raises:
            ValueError: If mpan or serial_number is not provided and not found
                in environment
        """
        if mpan is None:
            mpan = os.getenv("OCTOPUS_ELECTRICITY_MPAN")
            if mpan is None:
                msg = (
                    "mpan is required. Provide it as an argument or set "
                    "OCTOPUS_ELECTRICITY_MPAN environment variable."
                )
                raise ValueError(msg)

        if serial_number is None:
            serial_number = os.getenv("OCTOPUS_ELECTRICITY_SERIAL_NUMBER")
            if serial_number is None:
                msg = (
                    "serial_number is required. Provide it as an argument or "
                    "set OCTOPUS_ELECTRICITY_SERIAL_NUMBER environment variable."
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

        endpoint = (
            f"electricity-meter-points/{mpan}/meters/{serial_number}/consumption/"
        )
        results = self.client.get_paginated(endpoint, params)
        return [Consumption.model_validate(item) for item in results]
