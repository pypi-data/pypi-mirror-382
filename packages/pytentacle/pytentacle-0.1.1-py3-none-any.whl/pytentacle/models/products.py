"""Product models."""

from datetime import datetime

from pydantic import BaseModel, Field

from pytentacle.models.tariffs import (
    Eco7ElectricityTariff,
    GasTariff,
    StandardElectricityTariff,
)


class Product(BaseModel):
    """Energy product with associated tariffs.

    Products have multiple tariff variants based on:
    - GSP (Grid Supply Point) - 14 regional zones in UK
    - Payment method (direct debit, prepay, etc.)
    - Register type (single vs dual for electricity)
    """

    code: str = Field(description="Product code (e.g., 'AGILE-24-04-03')")
    direction: str | None = Field(
        None,
        description="Direction (IMPORT for consumption, EXPORT for generation)",
    )
    full_name: str = Field(description="Full product name")
    display_name: str = Field(description="Display name")
    description: str = Field(description="Product description")
    is_variable: bool = Field(description="Whether the product has variable rates")
    is_green: bool = Field(description="Whether the product is 100% renewable")
    is_tracker: bool = Field(description="Whether the product tracks wholesale prices")
    is_prepay: bool = Field(description="Whether the product is prepayment")
    is_business: bool = Field(description="Whether the product is for business")
    is_restricted: bool = Field(
        description="Whether the product has restricted availability",
    )
    term: int | None = Field(None, description="Contract term in months")
    available_from: datetime = Field(description="Date product became available")
    available_to: datetime | None = Field(
        None,
        description="Date product is available until",
    )
    links: list[dict[str, str]] = Field(
        default_factory=list,
        description="HATEOAS links",
    )
    brand: str = Field(description="Brand name")

    # Tariffs - these are populated when fetching a specific product
    # Structure: dict with GSP keys, each containing payment_method: tariff_data
    single_register_electricity_tariffs: dict[
        str,
        dict[str, StandardElectricityTariff],
    ] = Field(
        default_factory=dict,
        description="Single register electricity tariffs by GSP and payment method",
    )
    dual_register_electricity_tariffs: dict[str, dict[str, Eco7ElectricityTariff]] = (
        Field(
            default_factory=dict,
            description=(
                "Dual register (Economy 7) electricity tariffs by GSP "
                "and payment method"
            ),
        )
    )
    single_register_gas_tariffs: dict[str, dict[str, GasTariff]] = Field(
        default_factory=dict,
        description="Gas tariffs by GSP and payment method",
    )
    sample_quotes: dict[str, dict[str, dict[str, dict[str, int]]]] | None = Field(
        None,
        description=(
            "Sample cost calculations by GSP, payment method, and consumption type"
        ),
    )
    sample_consumption: dict[str, dict[str, int]] | None = Field(
        None,
        description="Standard consumption values used for quotes",
    )
