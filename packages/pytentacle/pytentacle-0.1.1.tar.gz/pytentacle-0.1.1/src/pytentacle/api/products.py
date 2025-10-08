"""Products API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytentacle.models.products import Product
from pytentacle.models.tariffs import HistoricalCharge

if TYPE_CHECKING:
    import builtins
    from datetime import datetime

    from pytentacle.core.base import BaseClient


class ProductsAPI:
    """Products API endpoints.

    Provides access to energy products and their tariff rates.
    """

    def __init__(self, client: BaseClient) -> None:
        """Initialize the products API.

        Args:
            client: The HTTP client to use
        """
        self.client = client

    def list(  # noqa: PLR0913
        self,
        *,
        is_variable: bool | None = None,
        is_green: bool | None = None,
        is_tracker: bool | None = None,
        is_prepay: bool | None = None,
        is_business: bool | None = None,
        available_at: datetime | None = None,
    ) -> list[Product]:
        """List all available products.

        Args:
            is_variable: Filter by variable rate products
            is_green: Filter by green/renewable products
            is_tracker: Filter by tracker products
            is_prepay: Filter by prepayment products
            is_business: Filter by business products
            available_at: Filter by products available at this date

        Returns:
            List of Product objects
        """
        params = {}
        if is_variable is not None:
            params["is_variable"] = str(is_variable).lower()
        if is_green is not None:
            params["is_green"] = str(is_green).lower()
        if is_tracker is not None:
            params["is_tracker"] = str(is_tracker).lower()
        if is_prepay is not None:
            params["is_prepay"] = str(is_prepay).lower()
        if is_business is not None:
            params["is_business"] = str(is_business).lower()
        if available_at is not None:
            params["available_at"] = available_at.isoformat()

        results = self.client.get_paginated("products/", params)
        return [Product.model_validate(item) for item in results]

    def get(self, product_code: str) -> Product:
        """Get detailed information about a specific product.

        Args:
            product_code: The product code (e.g., 'AGILE-24-04-03')

        Returns:
            Product object with all tariff details
        """
        data = self.client.get(f"products/{product_code}/")
        return Product.model_validate(data)

    def get_electricity_standard_unit_rates(
        self,
        product_code: str,
        tariff_code: str,
        *,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        page_size: int | None = None,
    ) -> builtins.list[HistoricalCharge]:
        """Get standard electricity unit rates for a tariff.

        Args:
            product_code: The product code
            tariff_code: The tariff code (e.g., 'E-1R-AGILE-24-04-03-A')
            period_from: Filter rates from this datetime (inclusive)
            period_to: Filter rates to this datetime (exclusive)
            page_size: Number of results per page (max 1500)

        Returns:
            List of HistoricalCharge objects
        """
        params: dict[str, str | int] = {}
        if period_from:
            params["period_from"] = period_from.isoformat()
        if period_to:
            params["period_to"] = period_to.isoformat()
        if page_size:
            params["page_size"] = page_size

        endpoint = (
            f"products/{product_code}/electricity-tariffs/{tariff_code}/"
            "standard-unit-rates/"
        )
        results = self.client.get_paginated(endpoint, params)
        return [HistoricalCharge.model_validate(item) for item in results]

    def get_electricity_day_unit_rates(
        self,
        product_code: str,
        tariff_code: str,
        *,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        page_size: int | None = None,
    ) -> builtins.list[HistoricalCharge]:
        """Get day unit rates for Economy 7 electricity tariff.

        Args:
            product_code: The product code
            tariff_code: The tariff code
            period_from: Filter rates from this datetime (inclusive)
            period_to: Filter rates to this datetime (exclusive)
            page_size: Number of results per page (max 1500)

        Returns:
            List of HistoricalCharge objects
        """
        params: dict[str, str | int] = {}
        if period_from:
            params["period_from"] = period_from.isoformat()
        if period_to:
            params["period_to"] = period_to.isoformat()
        if page_size:
            params["page_size"] = page_size

        endpoint = (
            f"products/{product_code}/electricity-tariffs/{tariff_code}/day-unit-rates/"
        )
        results = self.client.get_paginated(endpoint, params)
        return [HistoricalCharge.model_validate(item) for item in results]

    def get_electricity_night_unit_rates(
        self,
        product_code: str,
        tariff_code: str,
        *,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        page_size: int | None = None,
    ) -> builtins.list[HistoricalCharge]:
        """Get night unit rates for Economy 7 electricity tariff.

        Args:
            product_code: The product code
            tariff_code: The tariff code
            period_from: Filter rates from this datetime (inclusive)
            period_to: Filter rates to this datetime (exclusive)
            page_size: Number of results per page (max 1500)

        Returns:
            List of HistoricalCharge objects
        """
        params: dict[str, str | int] = {}
        if period_from:
            params["period_from"] = period_from.isoformat()
        if period_to:
            params["period_to"] = period_to.isoformat()
        if page_size:
            params["page_size"] = page_size

        endpoint = (
            f"products/{product_code}/electricity-tariffs/{tariff_code}/"
            "night-unit-rates/"
        )
        results = self.client.get_paginated(endpoint, params)
        return [HistoricalCharge.model_validate(item) for item in results]

    def get_electricity_standing_charges(
        self,
        product_code: str,
        tariff_code: str,
        *,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        page_size: int | None = None,
    ) -> builtins.list[HistoricalCharge]:
        """Get electricity standing charges for a tariff.

        Args:
            product_code: The product code
            tariff_code: The tariff code
            period_from: Filter charges from this datetime (inclusive)
            period_to: Filter charges to this datetime (exclusive)
            page_size: Number of results per page (max 1500)

        Returns:
            List of HistoricalCharge objects
        """
        params: dict[str, str | int] = {}
        if period_from:
            params["period_from"] = period_from.isoformat()
        if period_to:
            params["period_to"] = period_to.isoformat()
        if page_size:
            params["page_size"] = page_size

        endpoint = (
            f"products/{product_code}/electricity-tariffs/{tariff_code}/"
            "standing-charges/"
        )
        results = self.client.get_paginated(endpoint, params)
        return [HistoricalCharge.model_validate(item) for item in results]

    def get_gas_standard_unit_rates(
        self,
        product_code: str,
        tariff_code: str,
        *,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        page_size: int | None = None,
    ) -> builtins.list[HistoricalCharge]:
        """Get gas unit rates for a tariff.

        Args:
            product_code: The product code
            tariff_code: The tariff code (e.g., 'G-1R-AGILE-24-04-03-A')
            period_from: Filter rates from this datetime (inclusive)
            period_to: Filter rates to this datetime (exclusive)
            page_size: Number of results per page (max 1500)

        Returns:
            List of HistoricalCharge objects
        """
        params: dict[str, str | int] = {}
        if period_from:
            params["period_from"] = period_from.isoformat()
        if period_to:
            params["period_to"] = period_to.isoformat()
        if page_size:
            params["page_size"] = page_size

        endpoint = (
            f"products/{product_code}/gas-tariffs/{tariff_code}/standard-unit-rates/"
        )
        results = self.client.get_paginated(endpoint, params)
        return [HistoricalCharge.model_validate(item) for item in results]

    def get_gas_standing_charges(
        self,
        product_code: str,
        tariff_code: str,
        *,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        page_size: int | None = None,
    ) -> builtins.list[HistoricalCharge]:
        """Get gas standing charges for a tariff.

        Args:
            product_code: The product code
            tariff_code: The tariff code
            period_from: Filter charges from this datetime (inclusive)
            period_to: Filter charges to this datetime (exclusive)
            page_size: Number of results per page (max 1500)

        Returns:
            List of HistoricalCharge objects
        """
        params: dict[str, str | int] = {}
        if period_from:
            params["period_from"] = period_from.isoformat()
        if period_to:
            params["period_to"] = period_to.isoformat()
        if page_size:
            params["page_size"] = page_size

        endpoint = (
            f"products/{product_code}/gas-tariffs/{tariff_code}/standing-charges/"
        )
        results = self.client.get_paginated(endpoint, params)
        return [HistoricalCharge.model_validate(item) for item in results]
