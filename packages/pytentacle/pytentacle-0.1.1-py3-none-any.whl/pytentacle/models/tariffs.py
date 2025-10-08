"""Tariff models."""

from datetime import datetime

from pydantic import BaseModel, Field


class HistoricalCharge(BaseModel):
    """Historical tariff charge (unit rate or standing charge).

    Represents a price that was valid during a specific time period.
    """

    value_exc_vat: float = Field(description="Price excluding VAT")
    value_inc_vat: float = Field(description="Price including VAT")
    valid_from: datetime = Field(description="Start of validity period")
    valid_to: datetime | None = Field(None, description="End of validity period")
    payment_method: str | None = Field(
        None,
        description="Payment method this charge applies to",
    )


class StandardElectricityTariff(BaseModel):
    """Single register electricity tariff.

    Standard tariffs have one rate that applies all day.
    """

    code: str = Field(description="Tariff code (e.g., E-1R-AGILE-24-04-03-A)")
    standing_charge_exc_vat: float = Field(description="Daily standing charge exc VAT")
    standing_charge_inc_vat: float = Field(description="Daily standing charge inc VAT")
    online_discount_exc_vat: float = Field(description="Online discount exc VAT")
    online_discount_inc_vat: float = Field(description="Online discount inc VAT")
    dual_fuel_discount_exc_vat: float = Field(
        description="Dual fuel discount exc VAT",
    )
    dual_fuel_discount_inc_vat: float = Field(
        description="Dual fuel discount inc VAT",
    )
    exit_fees_exc_vat: float = Field(description="Exit fees exc VAT")
    exit_fees_inc_vat: float = Field(description="Exit fees inc VAT")
    exit_fees_type: str = Field(
        description="Exit fee type (e.g., 'NONE', 'PER_FUEL')",
    )
    links: list[dict[str, str]] = Field(
        default_factory=list,
        description="HATEOAS links to rate endpoints",
    )


class Eco7ElectricityTariff(BaseModel):
    """Dual register electricity tariff (Economy 7).

    Economy 7 tariffs have different rates for day and night usage.
    """

    code: str = Field(description="Tariff code")
    standing_charge_exc_vat: float = Field(description="Daily standing charge exc VAT")
    standing_charge_inc_vat: float = Field(description="Daily standing charge inc VAT")
    online_discount_exc_vat: float = Field(description="Online discount exc VAT")
    online_discount_inc_vat: float = Field(description="Online discount inc VAT")
    dual_fuel_discount_exc_vat: float = Field(
        description="Dual fuel discount exc VAT",
    )
    dual_fuel_discount_inc_vat: float = Field(
        description="Dual fuel discount inc VAT",
    )
    exit_fees_exc_vat: float = Field(description="Exit fees exc VAT")
    exit_fees_inc_vat: float = Field(description="Exit fees inc VAT")
    exit_fees_type: str = Field(description="Exit fee type")
    links: list[dict[str, str]] = Field(
        default_factory=list,
        description="HATEOAS links to rate endpoints",
    )
    day_unit_rate_exc_vat: float | None = Field(
        None,
        description="Day unit rate exc VAT",
    )
    day_unit_rate_inc_vat: float | None = Field(
        None,
        description="Day unit rate inc VAT",
    )
    night_unit_rate_exc_vat: float | None = Field(
        None,
        description="Night unit rate exc VAT",
    )
    night_unit_rate_inc_vat: float | None = Field(
        None,
        description="Night unit rate inc VAT",
    )


class GasTariff(BaseModel):
    """Gas tariff."""

    code: str = Field(description="Tariff code (e.g., G-1R-AGILE-24-04-03-A)")
    standing_charge_exc_vat: float = Field(description="Daily standing charge exc VAT")
    standing_charge_inc_vat: float = Field(description="Daily standing charge inc VAT")
    online_discount_exc_vat: float = Field(description="Online discount exc VAT")
    online_discount_inc_vat: float = Field(description="Online discount inc VAT")
    dual_fuel_discount_exc_vat: float = Field(
        description="Dual fuel discount exc VAT",
    )
    dual_fuel_discount_inc_vat: float = Field(
        description="Dual fuel discount inc VAT",
    )
    exit_fees_exc_vat: float = Field(description="Exit fees exc VAT")
    exit_fees_inc_vat: float = Field(description="Exit fees inc VAT")
    exit_fees_type: str = Field(description="Exit fee type")
    links: list[dict[str, str]] = Field(
        default_factory=list,
        description="HATEOAS links to rate endpoints",
    )
    unit_rate_exc_vat: float | None = Field(None, description="Unit rate exc VAT")
    unit_rate_inc_vat: float | None = Field(None, description="Unit rate inc VAT")
