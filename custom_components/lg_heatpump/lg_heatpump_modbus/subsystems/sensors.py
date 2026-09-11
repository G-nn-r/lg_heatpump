"""Physical measurements the outdoor and indoor units report (input registers).

Every value here is read-only: input registers cannot be written. Addresses are
the protocol addresses, i.e. input register 1 of the documentation is address 0.
"""

from __future__ import annotations

from ..data_model import (
    BAR,
    HERTZ,
    LITRES_PER_MINUTE,
    LgComponent,
    enum_value,
    gauge,
    integer,
    temperature,
)
from ..enums import EnergyState

SECONDS_PER_MINUTE = 60


class Sensors(LgComponent):
    """Temperatures, pressures and running state, read in one block."""

    register_space = "input"
    register_ranges = ((0, 24),)

    error_code = integer(
        0, signed=False, description="Active error code; 0 when no error is active"
    )
    """Active error code reported by the outdoor unit."""

    odu_operation_cycle = integer(
        1, signed=False, description="Outdoor-unit operation cycle"
    )
    """Raw outdoor-unit operation cycle code."""

    water_inlet_temperature = temperature(
        2, description="Water temperature entering the heat pump"
    )
    """Water inlet temperature."""

    water_outlet_temperature = temperature(
        3, description="Water temperature leaving the heat pump"
    )
    """Water outlet temperature."""

    backup_heater_outlet_temperature = temperature(
        4, description="Water temperature leaving the backup heater"
    )
    """Backup heater outlet temperature."""

    dhw_tank_temperature = temperature(
        5, description="Domestic hot water tank temperature"
    )
    """Domestic hot water tank temperature."""

    solar_collector_temperature = temperature(
        6, description="Solar collector temperature"
    )
    """Solar collector temperature."""

    room_air_temperature_circuit_1 = temperature(
        7, description="Room air temperature measured for circuit 1"
    )
    """Room air temperature of circuit 1."""

    water_flow_rate = gauge(
        8,
        0.1,
        signed=False,
        unit=LITRES_PER_MINUTE,
        digits=1,
        description="Water flow rate through the heat pump",
    )
    """Water flow rate."""

    water_outlet_temperature_circuit_2 = temperature(
        9, description="Water temperature leaving circuit 2"
    )
    """Water outlet temperature of circuit 2."""

    room_air_temperature_circuit_2 = temperature(
        10, description="Room air temperature measured for circuit 2"
    )
    """Room air temperature of circuit 2."""

    energy_state = enum_value(
        11, EnergyState, description="Smart-grid energy state currently in effect"
    )
    """Smart-grid energy state currently in effect."""

    outdoor_temperature = temperature(12, description="Outdoor air temperature")
    """Outdoor air temperature."""

    liquid_pipe_temperature = temperature(
        16, scale=1, digits=0, description="Refrigerant liquid pipe temperature"
    )
    """Refrigerant liquid pipe temperature."""

    suction_temperature = temperature(
        18, scale=1, digits=0, description="Compressor suction temperature"
    )
    """Compressor suction temperature."""

    discharge_temperature = temperature(
        19, scale=1, digits=0, description="Compressor discharge temperature"
    )
    """Compressor discharge temperature."""

    evaporator_inlet_temperature = temperature(
        20, description="Refrigerant temperature entering the evaporator"
    )
    """Evaporator inlet temperature."""

    evaporator_outlet_temperature = temperature(
        21, description="Refrigerant temperature leaving the evaporator"
    )
    """Evaporator outlet temperature."""

    high_pressure = integer(
        22, signed=False, unit=BAR, description="Condenser (high side) pressure"
    )
    """Condenser (high side) pressure."""

    low_pressure = integer(
        23, signed=False, unit=BAR, description="Evaporator (low side) pressure"
    )
    """Evaporator (low side) pressure."""

    compressor_frequency = integer(
        24, signed=False, unit=HERTZ, description="Compressor rotation frequency"
    )
    """Compressor rotation frequency, in revolutions per second."""

    @property
    def compressor_speed(self) -> int | None:
        """Return the compressor speed in revolutions per minute."""
        if (frequency := self.compressor_frequency) is None:
            return None
        return frequency * SECONDS_PER_MINUTE

    @property
    def water_temperature_difference(self) -> float | None:
        """Return the spread between the water outlet and inlet, in kelvin."""
        outlet = self.water_outlet_temperature
        inlet = self.water_inlet_temperature
        if outlet is None or inlet is None:
            return None
        return round(outlet - inlet, 1)
