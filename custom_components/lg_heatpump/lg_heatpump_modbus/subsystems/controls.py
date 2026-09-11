"""Setpoints and operating modes (holding registers).

These are the values a controller writes. Reading them back is how the heat
pump reports what it is currently configured to do.
"""

from __future__ import annotations

from ..data_model import LgComponent, enum_value, integer, temperature
from ..enums import ControlMethod, EnergyState, OperationMode

#: Protocol limits for the water setpoints, in degrees Celsius. The range an
#: installation actually accepts is narrower and set by the installer.
WATER_SETPOINT_MIN = 15.0
WATER_SETPOINT_MAX = 65.0

#: Protocol limits for the room air setpoints, in degrees Celsius.
ROOM_SETPOINT_MIN = 16.0
ROOM_SETPOINT_MAX = 30.0

#: Protocol limits for the domestic hot water setpoint, in degrees Celsius.
DHW_SETPOINT_MIN = 30.0
DHW_SETPOINT_MAX = 80.0

#: Protocol limits for the auto-mode setpoint shift, in kelvin.
SHIFT_MIN = -5
SHIFT_MAX = 5

KELVIN = "K"


class Controls(LgComponent):
    """Operating mode, control method and every writable setpoint."""

    register_space = "holding"
    register_ranges = ((0, 9),)

    operation_mode = enum_value(
        0,
        OperationMode,
        writable=True,
        description="Requested operation mode",
    )
    """Requested operation mode."""

    control_method = enum_value(
        1,
        ControlMethod,
        writable=True,
        description="Temperature the controller regulates on",
    )
    """Temperature the controller regulates on."""

    target_temperature_circuit_1 = temperature(
        2,
        writable=True,
        min_value=WATER_SETPOINT_MIN,
        max_value=WATER_SETPOINT_MAX,
        description="Water target temperature for circuit 1",
    )
    """Water target temperature of circuit 1."""

    room_air_setpoint_circuit_1 = temperature(
        3,
        writable=True,
        min_value=ROOM_SETPOINT_MIN,
        max_value=ROOM_SETPOINT_MAX,
        description="Room air target temperature for circuit 1",
    )
    """Room air target temperature of circuit 1."""

    shift_in_auto_mode_circuit_1 = integer(
        4,
        signed=True,
        unit=KELVIN,
        writable=True,
        min_value=SHIFT_MIN,
        max_value=SHIFT_MAX,
        description="Weather-compensation setpoint shift for circuit 1",
    )
    """Weather-compensation setpoint shift of circuit 1."""

    target_temperature_circuit_2 = temperature(
        5,
        writable=True,
        min_value=WATER_SETPOINT_MIN,
        max_value=WATER_SETPOINT_MAX,
        description="Water target temperature for circuit 2",
    )
    """Water target temperature of circuit 2."""

    room_air_setpoint_circuit_2 = temperature(
        6,
        writable=True,
        min_value=ROOM_SETPOINT_MIN,
        max_value=ROOM_SETPOINT_MAX,
        description="Room air target temperature for circuit 2",
    )
    """Room air target temperature of circuit 2."""

    shift_in_auto_mode_circuit_2 = integer(
        7,
        signed=True,
        unit=KELVIN,
        writable=True,
        min_value=SHIFT_MIN,
        max_value=SHIFT_MAX,
        description="Weather-compensation setpoint shift for circuit 2",
    )
    """Weather-compensation setpoint shift of circuit 2."""

    dhw_target_temperature = temperature(
        8,
        writable=True,
        min_value=DHW_SETPOINT_MIN,
        max_value=DHW_SETPOINT_MAX,
        description="Domestic hot water target temperature",
    )
    """Domestic hot water target temperature."""

    energy_state = enum_value(
        9, EnergyState, description="Smart-grid energy state as configured"
    )
    """Smart-grid energy state as configured."""

    def target_temperature(self, circuit: int) -> float | None:
        """Return the water target temperature of ``circuit`` (1 or 2)."""
        return getattr(self, f"target_temperature_circuit_{_check(circuit)}")

    def room_air_setpoint(self, circuit: int) -> float | None:
        """Return the room air target temperature of ``circuit`` (1 or 2)."""
        return getattr(self, f"room_air_setpoint_circuit_{_check(circuit)}")

    def shift_in_auto_mode(self, circuit: int) -> int | None:
        """Return the setpoint shift of ``circuit`` (1 or 2)."""
        return getattr(self, f"shift_in_auto_mode_circuit_{_check(circuit)}")

    async def set_target_temperature(self, circuit: int, value: float) -> None:
        """Write the water target temperature of ``circuit`` (1 or 2)."""
        await self.write(f"target_temperature_circuit_{_check(circuit)}", value)

    async def set_room_air_setpoint(self, circuit: int, value: float) -> None:
        """Write the room air target temperature of ``circuit`` (1 or 2)."""
        await self.write(f"room_air_setpoint_circuit_{_check(circuit)}", value)

    async def set_shift_in_auto_mode(self, circuit: int, value: int) -> None:
        """Write the setpoint shift of ``circuit`` (1 or 2)."""
        await self.write(f"shift_in_auto_mode_circuit_{_check(circuit)}", value)

    async def set_operation_mode(self, mode: OperationMode) -> None:
        """Write the requested operation mode."""
        await self.write("operation_mode", mode)

    async def set_control_method(self, method: ControlMethod) -> None:
        """Write the temperature the controller regulates on."""
        await self.write("control_method", method)

    async def set_dhw_target_temperature(self, value: float) -> None:
        """Write the domestic hot water target temperature."""
        await self.write("dhw_target_temperature", value)


def _check(circuit: int) -> int:
    """Return ``circuit`` if it names a circuit this device can have."""
    if circuit not in (1, 2):
        raise ValueError(f"Circuit must be 1 or 2, got {circuit}")
    return circuit
