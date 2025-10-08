"""Pytentacle - Modern Python client for the Octopus Energy API.

This library provides both synchronous and asynchronous clients for
interacting with the Octopus Energy API.

Example:
    ```python
    from pytentacle import OctopusClient

    client = OctopusClient(api_key="your_api_key")
    products = client.products.list()
    client.close()
    ```

    Or with async:
    ```python
    from pytentacle import AsyncOctopusClient

    async with AsyncOctopusClient(api_key="your_api_key") as client:
        products = await client.products.list()
    ```
"""

from pytentacle.async_client import AsyncOctopusClient
from pytentacle.client import OctopusClient
from pytentacle.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PytentacleError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from pytentacle.models import (
    Consumption,
    Eco7ElectricityTariff,
    ElectricityMeterPoint,
    GasTariff,
    GridSupplyPoint,
    HistoricalCharge,
    Product,
    StandardElectricityTariff,
)

__version__ = "0.1.1"

__all__ = [
    "APIError",
    "AsyncOctopusClient",
    "AuthenticationError",
    "Consumption",
    "Eco7ElectricityTariff",
    "ElectricityMeterPoint",
    "GasTariff",
    "GridSupplyPoint",
    "HistoricalCharge",
    "NotFoundError",
    "OctopusClient",
    "Product",
    "PytentacleError",
    "RateLimitError",
    "ServerError",
    "StandardElectricityTariff",
    "ValidationError",
]
