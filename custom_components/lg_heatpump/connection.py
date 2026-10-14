"""Modbus connection settings for the LG Heat Pump integration.

The connection itself is not owned here: Home Assistant's ``modbus`` integration
hands out units over connections it shares between integrations, so this
integration cannot compete with another one talking to the same gateway. This
module only turns the stored config into the parameters it asks with.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection import ModbusTcpParams

from homeassistant.const import CONF_HOST, CONF_PORT

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


def create_modbus_params(data: Mapping[str, Any]) -> ModbusTcpParams:
    """Return the Modbus TCP link settings stored in a config entry or flow."""
    return ModbusTcpParams(host=data[CONF_HOST], port=data[CONF_PORT])
