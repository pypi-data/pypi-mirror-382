"""Tests for Products API endpoints."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from pytentacle.api.products import ProductsAPI
from pytentacle.models.products import Product
from pytentacle.models.tariffs import HistoricalCharge


@pytest.fixture
def products_api() -> ProductsAPI:
    """Return a products API instance with mocked client."""
    client = MagicMock()
    return ProductsAPI(client)


@pytest.fixture
def mock_product_data() -> dict:
    """Return mock product data."""
    return {
        "code": "AGILE-24-04-03",
        "direction": "IMPORT",
        "full_name": "Agile Octopus April 2024 v1",
        "display_name": "Agile Octopus",
        "description": "Agile Octopus gives you half-hourly tariffs.",
        "is_variable": True,
        "is_green": True,
        "is_tracker": False,
        "is_prepay": False,
        "is_business": False,
        "is_restricted": False,
        "term": 12,
        "available_from": "2024-04-03T00:00:00Z",
        "available_to": None,
        "links": [],
        "brand": "OCTOPUS_ENERGY",
    }


@pytest.fixture
def mock_charge_data() -> dict:
    """Return mock historical charge data."""
    return {
        "value_exc_vat": 15.5,
        "value_inc_vat": 16.275,
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": "2024-01-01T00:30:00Z",
        "payment_method": "DIRECT_DEBIT",
    }


class TestProductsList:
    """Tests for products list method."""

    def test_list_no_filters(
        self, products_api: ProductsAPI, mock_product_data: dict
    ) -> None:
        """Test listing products without filters."""
        products_api.client.get_paginated.return_value = [mock_product_data]  # type: ignore[attr-defined]

        result = products_api.list()

        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "products/", {}
        )
        assert len(result) == 1
        assert isinstance(result[0], Product)
        assert result[0].code == "AGILE-24-04-03"

    def test_list_with_is_variable(
        self, products_api: ProductsAPI, mock_product_data: dict
    ) -> None:
        """Test listing products filtered by is_variable."""
        products_api.client.get_paginated.return_value = [mock_product_data]  # type: ignore[attr-defined]

        result = products_api.list(is_variable=True)

        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "products/", {"is_variable": "true"}
        )
        assert len(result) == 1

    def test_list_with_is_green(
        self, products_api: ProductsAPI, mock_product_data: dict
    ) -> None:
        """Test listing products filtered by is_green."""
        products_api.client.get_paginated.return_value = [mock_product_data]  # type: ignore[attr-defined]

        result = products_api.list(is_green=True)

        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "products/", {"is_green": "true"}
        )
        assert len(result) == 1

    def test_list_with_is_tracker(
        self, products_api: ProductsAPI, mock_product_data: dict
    ) -> None:
        """Test listing products filtered by is_tracker."""
        products_api.client.get_paginated.return_value = [mock_product_data]  # type: ignore[attr-defined]

        result = products_api.list(is_tracker=False)

        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "products/", {"is_tracker": "false"}
        )
        assert len(result) == 1

    def test_list_with_is_prepay(
        self, products_api: ProductsAPI, mock_product_data: dict
    ) -> None:
        """Test listing products filtered by is_prepay."""
        products_api.client.get_paginated.return_value = [mock_product_data]  # type: ignore[attr-defined]

        result = products_api.list(is_prepay=True)

        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "products/", {"is_prepay": "true"}
        )
        assert len(result) == 1

    def test_list_with_is_business(
        self, products_api: ProductsAPI, mock_product_data: dict
    ) -> None:
        """Test listing products filtered by is_business."""
        products_api.client.get_paginated.return_value = [mock_product_data]  # type: ignore[attr-defined]

        result = products_api.list(is_business=False)

        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "products/", {"is_business": "false"}
        )
        assert len(result) == 1

    def test_list_with_available_at(
        self, products_api: ProductsAPI, mock_product_data: dict
    ) -> None:
        """Test listing products filtered by available_at."""
        products_api.client.get_paginated.return_value = [mock_product_data]  # type: ignore[attr-defined]
        available_at = datetime(2024, 4, 3, tzinfo=timezone.utc)

        result = products_api.list(available_at=available_at)

        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "products/", {"available_at": "2024-04-03T00:00:00+00:00"}
        )
        assert len(result) == 1

    def test_list_with_all_filters(
        self, products_api: ProductsAPI, mock_product_data: dict
    ) -> None:
        """Test listing products with all filters."""
        products_api.client.get_paginated.return_value = [mock_product_data]  # type: ignore[attr-defined]
        available_at = datetime(2024, 4, 3, tzinfo=timezone.utc)

        result = products_api.list(
            is_variable=True,
            is_green=True,
            is_tracker=False,
            is_prepay=False,
            is_business=False,
            available_at=available_at,
        )

        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            "products/",
            {
                "is_variable": "true",
                "is_green": "true",
                "is_tracker": "false",
                "is_prepay": "false",
                "is_business": "false",
                "available_at": "2024-04-03T00:00:00+00:00",
            },
        )
        assert len(result) == 1


class TestProductsGet:
    """Tests for products get method."""

    def test_get(self, products_api: ProductsAPI, mock_product_data: dict) -> None:
        """Test getting a specific product."""
        products_api.client.get.return_value = mock_product_data  # type: ignore[attr-defined]

        result = products_api.get("AGILE-24-04-03")

        products_api.client.get.assert_called_once_with("products/AGILE-24-04-03/")  # type: ignore[attr-defined]
        assert isinstance(result, Product)
        assert result.code == "AGILE-24-04-03"


class TestElectricityStandardUnitRates:
    """Tests for electricity standard unit rates method."""

    def test_get_electricity_standard_unit_rates_no_params(
        self, products_api: ProductsAPI, mock_charge_data: dict
    ) -> None:
        """Test getting electricity standard unit rates without optional params."""
        products_api.client.get_paginated.return_value = [mock_charge_data]  # type: ignore[attr-defined]

        result = products_api.get_electricity_standard_unit_rates(
            "AGILE-24-04-03", "E-1R-AGILE-24-04-03-A"
        )

        expected_endpoint = (
            "products/AGILE-24-04-03/electricity-tariffs/E-1R-AGILE-24-04-03-A/"
            "standard-unit-rates/"
        )
        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint, {}
        )
        assert len(result) == 1
        assert isinstance(result[0], HistoricalCharge)

    def test_get_electricity_standard_unit_rates_with_dates(
        self, products_api: ProductsAPI, mock_charge_data: dict
    ) -> None:
        """Test getting electricity standard unit rates with date filters."""
        products_api.client.get_paginated.return_value = [mock_charge_data]  # type: ignore[attr-defined]
        period_from = datetime(2024, 1, 1, tzinfo=timezone.utc)
        period_to = datetime(2024, 1, 31, tzinfo=timezone.utc)

        result = products_api.get_electricity_standard_unit_rates(
            "AGILE-24-04-03",
            "E-1R-AGILE-24-04-03-A",
            period_from=period_from,
            period_to=period_to,
        )

        expected_endpoint = (
            "products/AGILE-24-04-03/electricity-tariffs/E-1R-AGILE-24-04-03-A/"
            "standard-unit-rates/"
        )
        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint,
            {
                "period_from": "2024-01-01T00:00:00+00:00",
                "period_to": "2024-01-31T00:00:00+00:00",
            },
        )
        assert len(result) == 1

    def test_get_electricity_standard_unit_rates_with_page_size(
        self, products_api: ProductsAPI, mock_charge_data: dict
    ) -> None:
        """Test getting electricity standard unit rates with page size."""
        products_api.client.get_paginated.return_value = [mock_charge_data]  # type: ignore[attr-defined]

        result = products_api.get_electricity_standard_unit_rates(
            "AGILE-24-04-03", "E-1R-AGILE-24-04-03-A", page_size=1000
        )

        expected_endpoint = (
            "products/AGILE-24-04-03/electricity-tariffs/E-1R-AGILE-24-04-03-A/"
            "standard-unit-rates/"
        )
        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint, {"page_size": 1000}
        )
        assert len(result) == 1


class TestElectricityDayUnitRates:
    """Tests for electricity day unit rates method."""

    def test_get_electricity_day_unit_rates(
        self, products_api: ProductsAPI, mock_charge_data: dict
    ) -> None:
        """Test getting electricity day unit rates."""
        products_api.client.get_paginated.return_value = [mock_charge_data]  # type: ignore[attr-defined]

        result = products_api.get_electricity_day_unit_rates(
            "VAR-24-04-03", "E-2R-VAR-24-04-03-A"
        )

        expected_endpoint = (
            "products/VAR-24-04-03/electricity-tariffs/E-2R-VAR-24-04-03-A/"
            "day-unit-rates/"
        )
        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint, {}
        )
        assert len(result) == 1
        assert isinstance(result[0], HistoricalCharge)


class TestElectricityNightUnitRates:
    """Tests for electricity night unit rates method."""

    def test_get_electricity_night_unit_rates(
        self, products_api: ProductsAPI, mock_charge_data: dict
    ) -> None:
        """Test getting electricity night unit rates."""
        products_api.client.get_paginated.return_value = [mock_charge_data]  # type: ignore[attr-defined]

        result = products_api.get_electricity_night_unit_rates(
            "VAR-24-04-03", "E-2R-VAR-24-04-03-A"
        )

        expected_endpoint = (
            "products/VAR-24-04-03/electricity-tariffs/E-2R-VAR-24-04-03-A/"
            "night-unit-rates/"
        )
        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint, {}
        )
        assert len(result) == 1
        assert isinstance(result[0], HistoricalCharge)


class TestElectricityStandingCharges:
    """Tests for electricity standing charges method."""

    def test_get_electricity_standing_charges(
        self, products_api: ProductsAPI, mock_charge_data: dict
    ) -> None:
        """Test getting electricity standing charges."""
        products_api.client.get_paginated.return_value = [mock_charge_data]  # type: ignore[attr-defined]

        result = products_api.get_electricity_standing_charges(
            "AGILE-24-04-03", "E-1R-AGILE-24-04-03-A"
        )

        expected_endpoint = (
            "products/AGILE-24-04-03/electricity-tariffs/E-1R-AGILE-24-04-03-A/"
            "standing-charges/"
        )
        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint, {}
        )
        assert len(result) == 1
        assert isinstance(result[0], HistoricalCharge)


class TestGasStandardUnitRates:
    """Tests for gas standard unit rates method."""

    def test_get_gas_standard_unit_rates(
        self, products_api: ProductsAPI, mock_charge_data: dict
    ) -> None:
        """Test getting gas standard unit rates."""
        products_api.client.get_paginated.return_value = [mock_charge_data]  # type: ignore[attr-defined]

        result = products_api.get_gas_standard_unit_rates(
            "VAR-24-04-03", "G-1R-VAR-24-04-03-A"
        )

        expected_endpoint = (
            "products/VAR-24-04-03/gas-tariffs/G-1R-VAR-24-04-03-A/standard-unit-rates/"
        )
        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint, {}
        )
        assert len(result) == 1
        assert isinstance(result[0], HistoricalCharge)


class TestGasStandingCharges:
    """Tests for gas standing charges method."""

    def test_get_gas_standing_charges(
        self, products_api: ProductsAPI, mock_charge_data: dict
    ) -> None:
        """Test getting gas standing charges."""
        products_api.client.get_paginated.return_value = [mock_charge_data]  # type: ignore[attr-defined]

        result = products_api.get_gas_standing_charges(
            "VAR-24-04-03", "G-1R-VAR-24-04-03-A"
        )

        expected_endpoint = (
            "products/VAR-24-04-03/gas-tariffs/G-1R-VAR-24-04-03-A/standing-charges/"
        )
        products_api.client.get_paginated.assert_called_once_with(  # type: ignore[attr-defined]
            expected_endpoint, {}
        )
        assert len(result) == 1
        assert isinstance(result[0], HistoricalCharge)
