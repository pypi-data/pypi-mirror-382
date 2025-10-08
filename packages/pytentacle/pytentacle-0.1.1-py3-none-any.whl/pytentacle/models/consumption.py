"""Consumption data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class Consumption(BaseModel):
    """Energy consumption data for a time period.

    Half-hourly data is only available for smart meters.
    - Electricity consumption is in kWh
    - Gas consumption units vary: kWh for SMETS1, m³ for SMETS2
    """

    consumption: float = Field(description="Energy consumption amount")
    interval_start: datetime = Field(
        description="Start of consumption interval (inclusive)",
    )
    interval_end: datetime = Field(
        description="End of consumption interval (exclusive)",
    )
