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
from ..enums import EnergyState, OduOperationCycle

SECONDS_PER_MINUTE = 60


class Sensors(LgComponent):
    """Temperatures, pressures and running state, read in one block."""

    register_space = "input"
    register_ranges = ((0, 12), (16, 16), (18, 24))

    # TODO verify
    # verified by G-nn-r: 0
    error_code = integer(
        0, signed=False, description="Active error code; 0 when no error is active"
    )
    """Active error code reported by the outdoor unit."""

    odu_operation_cycle = enum_value(
        1,
        OduOperationCycle,
        description="Outdoor-unit operation cycle",
    )
    """Outdoor-unit operation cycle state."""

    # TODO verify
    # verified by G-nn-r: 22.8, 24.9, 25.3, 25.7, 27.1, 27.8, 28.6, 29.3
    water_inlet_temperature = temperature(
        2, description="Water temperature entering the heat pump"
    )
    """Water inlet temperature."""

    # TODO verify
    # verified by G-nn-r: 22.8, 24.9, 25.7, 27.1, 27.8, 28.6, 30.8, 31.6, 32.4, 33.2
    water_outlet_temperature = temperature(
        3, description="Water temperature leaving the heat pump"
    )
    """Water outlet temperature."""

    # TODO verify
    # verified by G-nn-r: 23.2, 23.5, 25.3, 25.7, 26.4, 26.7, 27.8, 28.2, 28.6, 28.9, 29.7
    backup_heater_outlet_temperature = temperature(
        4, description="Water temperature leaving the backup heater"
    )
    """Backup heater outlet temperature."""

    # TODO verify
    #
    # verified by G-nn-r: 43.9, 48.8, 49.4
    dhw_tank_temperature = temperature(
        5, description="Domestic hot water tank temperature"
    )
    """
    Domestic hot water (DHW) tank temperature.
    In the LG ThinQ App, this can be found under Warmwasser -> Heißwassertemperatur
    """

    # TODO verify (G-nn-r has solar_pump=False, --> solar_collector_temperature is always 300.0 °C)
    # TODO decide whether this should be exposed when solar_pump=False. At least in HA, it should be unavailable
    solar_collector_temperature = temperature(
        6, description="Solar collector temperature"
    )
    """Solar collector temperature."""

    # TODO verify
    # this is always either 20.5 or 21.0 for G-nn-r, but does he have a sensor?
    room_air_temperature_circuit_1 = temperature(
        7, description="Room air temperature measured for circuit 1"
    )
    """Room air temperature of circuit 1."""

    # TODO verify value of 0 and ~5
    # verified by G-nn-r: 16.8, 16.9, 17.0, 17.2
    water_flow_rate = gauge(
        8,
        0.1,
        signed=False,
        unit=LITRES_PER_MINUTE,
        digits=1,
        description="Water flow rate through the heat pump",
    )
    """Water flow rate."""

    # TODO verify
    # verified by G-nn-r: 23.9, 24.2, 24.9, 25.7, 26.0, 26.4, 26.7, 27.1, 27.5, 27.8, 28.6, 29.7
    # TODO comment about relationship to water_outlet_temperature
    water_outlet_temperature_circuit_2 = temperature(
        9, description="Water temperature leaving circuit 2"
    )
    """Water outlet temperature of circuit 2."""

    # TODO verify
    # G-nn-r gets always -64.6 °C, is this the code for "not available"?
    room_air_temperature_circuit_2 = temperature(
        10, description="Room air temperature measured for circuit 2"
    )
    """Room air temperature of circuit 2."""

    # TODO verify
    # verified by G-nn-r: 0
    energy_state = enum_value(
        11, EnergyState, description="Smart-grid energy state currently in effect"
    )
    """Smart-grid energy state currently in effect."""

    # verified by G-nn-r: 15.5, 16.2, 16.5, 16.8, 17.2, 17.8, 18.1, 22.1, 22.4
    outdoor_temperature = temperature(12, description="Outdoor air temperature")
    """Outdoor air temperature."""

    # TODO is there water pressure on address 13?

    """
    TODO reorder heat gas temperatures: 
    Recommended Display Order
    Step	Temperature	                    Why It Matters
    1	    Suction temperature	            Refrigerant entering compressor; baseline before compression
    (compressor speed?)
    2	    Discharge temperature	        Compressor outlet; highest point in cycle; shows compression work
    3	    Liquid pipe temperature	        Condenser outlet; shows heat transferred to water; cooling from discharge
    4	    Evaporator inlet temperature	Lowest point after expansion device; temperature drop shows throttling
    5	    Evaporator outlet temperature	Outdoor coil exit; shows how much heat was absorbed; nearly same as suction
    """

    # TODO verify
    # 198-275 °C this is probably wrong scaled
    # This might be wrongly scaled? Expected values are 40-65 °C for R32, G-nn-r reports 198-275 °C
    liquid_pipe_temperature = temperature(
        16, scale=1, digits=0, description="Refrigerant liquid pipe temperature"
    )
    """Refrigerant liquid pipe temperature."""

    # TODO verify
    # This might be wrongly scaled? Expected values are -15 to +15 °C for R32, G-nn-r reports 97-278 °C
    # wrong scaling by factor of 10? See here, l. 154/187: https://github.com/basti242/homeassistant_lg_therma_v_modbus/pull/49/changes
    suction_temperature = temperature(
        18, scale=1, digits=0, description="Compressor suction temperature"
    )
    """Compressor suction temperature."""

    # TODO verify
    # This might be wrongly scaled? Expected values for CDT are 80-100°C (at max 65-110°C), G-nn-r reports 200-390, occasionally 700 °C.
    # "R32's critical temperature is 78.1°C. Above this point, R32 cannot exist as a distinct liquid or vapor—it becomes a supercritical fluid, and the entire refrigeration cycle breaks down."
    # Wrong scaling by a factor of 10? See here, l. 162/198: https://github.com/basti242/homeassistant_lg_therma_v_modbus/pull/49/changesö
    discharge_temperature = temperature(
        19, scale=1, digits=0, description="Compressor discharge temperature"
    )
    """Compressor discharge temperature."""

    # TODO verify
    # values range from 12.7 to 24.2 °C for G-nn-r, seems reasonable, but could also be correct for evaporator_outlet_temperature
    evaporator_inlet_temperature = temperature(
        20, description="Refrigerant temperature entering the evaporator"
    )
    """Evaporator inlet temperature."""

    # TODO verify
    # this is always equal to evaporator_inlet_temperature for G-nn-r, should only be the case when the compressor is off (otherwise an indication for no refrigerant flow or some other malfunction)
    evaporator_outlet_temperature = temperature(
        21, description="Refrigerant temperature leaving the evaporator"
    )
    """Evaporator outlet temperature."""

    # TODO verify
    # G-nn-r gets values of roughly 1100 to 1400 bar when the compressor is off and roughly 1800 to 2500 bar when the compressor is on,
    # this seems to be a scaling issue, probably factor of 100 wrong --> 11-14 bar / 18-25 bar would be reasonable
    # talk to basti242 about this, the list mentions °C: https://github.com/basti242/homeassistant_lg_therma_v_modbus/wiki/LG-Register-documentation
    # TODO refactor to high_pressure_refrigerant or refrigerant_high_pressure?
    high_pressure = integer(
        22, signed=False, unit=BAR, description="Condenser (high side) pressure"
    )
    """Condenser (high side) pressure."""

    # TODO verify
    # G-nn-r gets values of roughly 1100 to 1200 when the compressor is off and roughly 1200 to 1400 bar when the compressor is on,
    # this seems to be at least a scaling issue, probably factor of 100 wrong --> 11-12 bar / 12-14 bar would be MORE reasonable
    # but the difference to high_pressure should be near-zero for compressor off, low for low compressor speed and high for high compressor speed, which is not the case for G-nn-r's readings
    # talk to basti242 about this, the list mentions °C: https://github.com/basti242/homeassistant_lg_therma_v_modbus/wiki/LG-Register-documentation
    # TODO refactor to low_pressure_refrigerant or refrigerant_low_pressure?
    low_pressure = integer(
        23, signed=False, unit=BAR, description="Evaporator (low side) pressure"
    )
    """Evaporator (low side) pressure."""

    # TODO refactor to *_hz?
    # verified by G-nn-r: 0, 15, 27, 30, 35, 34, 43, 45. Maximum is expected at around ~50 Hz
    compressor_frequency = integer(
        24, signed=False, unit=HERTZ, description="Compressor rotation frequency"
    )
    """Compressor rotation frequency, in revolutions per second."""

    # verified by G-nn-r: 0, 900, 1620, 1800, 2040, 2100, 2580, 2700. Maximum is expected at around ~3000 rpm
    # TODO refactor to *_rpm?
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
