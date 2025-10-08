"""Tests for product models."""

from datetime import datetime

from pytentacle.models.products import Product


def test_product_model() -> None:
    """Test Product model validation."""
    data = {
        "code": "AGILE-24-04-03",
        "direction": "IMPORT",
        "full_name": "Agile Octopus April 2024",
        "display_name": "Agile Octopus",
        "description": "Variable tariff tracking wholesale prices",
        "is_variable": True,
        "is_green": True,
        "is_tracker": True,
        "is_prepay": False,
        "is_business": False,
        "is_restricted": False,
        "term": 12,
        "available_from": "2024-04-03T00:00:00Z",
        "available_to": None,
        "links": [],
        "brand": "OCTOPUS_ENERGY",
    }

    product = Product.model_validate(data)

    assert product.code == "AGILE-24-04-03"
    assert product.is_variable is True
    assert product.is_green is True
    assert product.brand == "OCTOPUS_ENERGY"
    assert isinstance(product.available_from, datetime)
    assert product.available_to is None
