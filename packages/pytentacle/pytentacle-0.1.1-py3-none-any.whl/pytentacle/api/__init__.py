"""API endpoint implementations."""

from pytentacle.api.electricity import ElectricityAPI
from pytentacle.api.gas import GasAPI
from pytentacle.api.industry import IndustryAPI
from pytentacle.api.products import ProductsAPI

__all__ = ["ElectricityAPI", "GasAPI", "IndustryAPI", "ProductsAPI"]
