"""Meter point models."""

from pydantic import BaseModel, Field


class ElectricityMeterPoint(BaseModel):
    """Electricity meter point details.

    MPAN (Meter Point Administration Number) uniquely identifies
    an electricity supply point in the UK.
    """

    mpan: str = Field(description="Meter Point Administration Number")
    profile_class: int = Field(
        description="Profile class (1-8, indicates usage pattern)",
    )
    consumption_standard: int | None = Field(
        default=None,
        description="Standard consumption in kWh",
    )
    gsp: str = Field(
        description="Grid Supply Point group ID (e.g., '_A', '_B', '_H')",
    )


class GasMeterPoint(BaseModel):
    """Gas meter point details.

    MPRN (Meter Point Reference Number) uniquely identifies
    a gas supply point in the UK.
    """

    mprn: str = Field(description="Meter Point Reference Number")
