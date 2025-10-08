"""Tests for consumption models."""

from datetime import datetime

from pytentacle.models.consumption import Consumption


def test_consumption_model() -> None:
    """Test Consumption model validation."""
    data = {
        "consumption": 0.123,
        "interval_start": "2024-01-01T00:00:00Z",
        "interval_end": "2024-01-01T00:30:00Z",
    }

    consumption = Consumption.model_validate(data)

    assert consumption.consumption == 0.123
    assert isinstance(consumption.interval_start, datetime)
    assert isinstance(consumption.interval_end, datetime)
