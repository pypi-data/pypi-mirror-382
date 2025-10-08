![Package version](https://img.shields.io/pypi/v/pytentacle)
![Python versions](https://img.shields.io/pypi/pyversions/pytentacle.svg)
![License](https://img.shields.io/pypi/l/pytentacle)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![py.typed](https://img.shields.io/badge/py-typed-FFD43B)
[![Coverage Status](https://coveralls.io/repos/github/samdobson/pytentacle/badge.svg?branch=main)](https://coveralls.io/github/samdobson/pytentacle?branch=main)

![Hero](hero.png)

# Pytentacle

Python client for the Octopus Energy API.

## Installation

```bash
pip install pytentacle
```

## Quick Start

```python
from pytentacle import OctopusClient

# Initialise the client (reads from OCTOPUS_API_KEY environment variable by default)
client = OctopusClient()

# Or pass the API key directly
# client = OctopusClient(api_key="your_api_key_here")

# List all available products
products = client.products.list()

# Get specific product details
product = client.products.get("AGILE-24-04-03")

# Get electricity consumption for a meter
consumption = client.electricity.get_consumption(
    mpan="1234567890123",
    serial_number="12A3456789",
    period_from="2024-01-01T00:00:00Z",
    period_to="2024-01-31T23:59:59Z"
)
```

## Async Support

```python
from pytentacle import AsyncOctopusClient

# Uses OCTOPUS_API_KEY environment variable by default
async with AsyncOctopusClient() as client:
    products = await client.products.list()
    product = await client.products.get("AGILE-24-04-03")
```

## Features

- ✅ Full type hints with Pydantic models
- ✅ Sync and async clients
- ✅ Automatic pagination handling
- ✅ Comprehensive error handling

## API Coverage

This library implements all publicly available Octopus Energy API endpoints:

- **Products** (8 endpoints) - List products, get tariff rates and standing charges
- **Electricity** (2 endpoints) - Meter point details and consumption data
- **Gas** (1 endpoint) - Gas consumption data
- **Industry** (1 endpoint) - Grid Supply Point lookups

Note: Partner-only endpoints (accounts, quotes) are not implemented.
