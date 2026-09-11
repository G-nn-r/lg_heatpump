"""Exceptions raised by lg-heatpump-modbus."""

from __future__ import annotations


class LgHeatPumpError(Exception):
    """Base class for every error this library raises itself."""


class LgValueValidationError(LgHeatPumpError, ValueError):
    """Raised when a value is outside the range the heat pump accepts."""


class LgFieldNotAvailableError(LgHeatPumpError, AttributeError):
    """Raised when a datapoint is not served by the configured model."""
