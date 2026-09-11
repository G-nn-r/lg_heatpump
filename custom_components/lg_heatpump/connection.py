"""Modbus connection handling for the LG Heat Pump custom integration.

Home Assistant core's ``modbus`` integration hands out units over connections it
shares between integrations, and a core integration should ask it for one. That
API is internal to core and carries no stability guarantee for a custom
integration installed through HACS, so this build wires its own connection
instead and keeps the shared-connection API for the move into core.

Everything else in this integration is unaffected: the device library only ever
sees a ``ModbusUnit``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


def async_create_connection(host: str, port: int) -> ModbusConnection:
    """Return a connection to a Modbus TCP endpoint.

    Building the connection performs no I/O, so a heat pump that is powered
    down does not stop the integration setting up: the first read opens the
    link, and a dropped link opens again on the next request.
    """
    return ModbusConnection(ModbusTcpParams(host=host, port=port))


def async_get_unit(connection: ModbusConnection, unit_id: int) -> ModbusUnit:
    """Return the unit handle for a station address on a connection."""
    return connection.for_unit(unit_id)
