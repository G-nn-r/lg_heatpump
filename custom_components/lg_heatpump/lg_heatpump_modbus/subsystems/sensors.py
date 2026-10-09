"""Physical measurements the outdoor and indoor units report (input registers, 0x04).

Every value here is read-only: input registers cannot be written. Addresses are
the protocol addresses, i.e. input register 1 of the documentation is address 0.

Some manuals have the address tables listed as holding registers (0x03), which is wrong, those would be read & write.
See also here: https://www.yourwizblog.com/blog/2022/02/20/therma-v-modbus-information/
"""

from __future__ import annotations

from ..data_model import (
    BAR,
    HERTZ,
    LITRES_PER_MINUTE,
    LgComponent,
    enum_value,
    gauge,
    hide_sentinel,
    integer,
    temperature,
)
from ..enums import EnergyState, OduOperationCycle

SECONDS_PER_MINUTE = 60

NO_AIR_THERMOMETER_CIRCUIT_2 = -64.6 # Dummy reading when there's no room_air_temperature_circuit_2 sensor fitted
NO_SOLAR_COLLECTOR_TEMPERATURE = 300.0  # Dummy reading for `solar_collector_temperature` without fitted solar collector
NO_WATER_PRESSURE = 0.0  # Dummy reading when there's no water pressure sensor fitted (typically for R32)

class Sensors(LgComponent):
    """Temperatures, pressures and running state, read in one block."""

    register_space = "input"
    register_ranges = ((0, 13), (16, 16), (18, 24))

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

    # verified by G-nn-r: 19.4, 20.8, 22.8, 23.9, 24.9, 22.2, 22.5, 24.2, 27.8, 28.6, 30.8, 30.1, 32.4, 34.0, 34.8, 41.0, 42.0, 42.9, 44.4, 45.0, 46.6, 48.8, 51.2
    water_inlet_temperature = temperature(
        2, description="Water temperature entering the heat pump"
    )
    """Water inlet temperature."""

    # verified by G-nn-r: 22.8, 23.5, 24.9, 24.2, 26.4, 22.2, 22.5, 27.1, 30.8, 30.1, 31.6, 33.2, 34.8, 35.7, 36.5, 42.9, 43.9, 47.1, 47.7, 50.0, 50.6, 52.4, 53.0, 55.7
    water_outlet_temperature = temperature(
        3, description="Water temperature leaving the heat pump"
    )
    """Water outlet temperature."""

    # verified by G-nn-r: 22.8, 23.2, 23.5, 24.2, 24.6, 25.3, 25.7, 26.4, 26.7, 27.8, 28.2, 28.6, 28.9, 29.3, 29.7, 30.1, 30.8, 31.2, 31.6, 34, 35.2, 44.0, 44.4, 46.0, 47.7, 50.0
    backup_heater_outlet_temperature = temperature(
        4, description="Water temperature leaving the backup heater"
    )
    """Backup heater outlet temperature."""

    # verified by G-nn-r: 39.6, 40.1, 40.5, 41.0, 42.0, 42.4, 42.9, 43.4, 43.9, 45.5, 46.0, 46.6, 47.1, 48.2, 48.8, 49.4, 50.6
    dhw_tank_temperature = temperature(
        5, description="Domestic hot water tank temperature"
    )
    """
    Domestic hot water (DHW) tank temperature.
    In the LG ThinQ App, this can be found under Warmwasser -> Heißwassertemperatur
    """

    # TODO verify non-sentinel values
    # verified by G-nn-r: no solar pump fitted -> always reads the 300 °C sentinel
    solar_collector_temperature = hide_sentinel(
        temperature(6, description="Solar collector temperature"),
        sentinel=NO_SOLAR_COLLECTOR_TEMPERATURE,
    )
    """
    Solar collector temperature.
    When no solar collector is fitted, the heat pump reports a fixed dummy value of
    300.0 °C instead of refusing the read; this decodes as ``None`` in that case.
    Set the component's (or the ``LgHeatPump``'s) ``debug`` attribute to see the
    raw 300.0 °C reading instead.
    """

    # TODO verify
    # this is always either 20.5, 21.0, or 21.5 for G-nn-r, but does he have a sensor? This might be either the control panel ("hp_temp_technikraum" in bastis integration) or the optional accessory PQRSTA0
    room_air_temperature_circuit_1 = temperature(
        7, description="Room air temperature measured for circuit 1"
    )
    """Room air temperature of circuit 1."""

    # TODO verify value of 0 and ~5
    # verified by G-nn-r: 5.0, 16.7, 16.8, 16.9, 17.0, 17.2, 17.3
    water_flow_rate = gauge(
        8,
        0.1,
        signed=False,
        unit=LITRES_PER_MINUTE,
        digits=1,
        description="Water flow rate through the heat pump",
    )
    """Water flow rate."""

    # verified by G-nn-r: 22.8, 23.2, 23.9, 24.2, 24.9, 25.7, 26.0, 26.4, 26.7, 27.1, 27.5, 27.8, 28.6, 28.9, 29.3, 29.7, 30.1, 30.5, 30.8, 31.2, 32.4
    # TODO comment about relationship to water_outlet_temperature
    water_outlet_temperature_circuit_2 = temperature(
        9, description="Water temperature leaving circuit 2"
    )
    """
    Water outlet temperature of circuit 2.
    Circuit 2 is cooler than circuit 1, it is mixing hot water (water_outlet_temperature) with cold water. 
    """

    # TODO verify non-sentinel values
    room_air_temperature_circuit_2 = hide_sentinel(
        temperature(10, description="Room air temperature measured for circuit 2"),
        sentinel=NO_AIR_THERMOMETER_CIRCUIT_2,
    )
    """
    Room air temperature of circuit 2.
    Without an air thermometer fitted for circuit 2, the heat pump reports a fixed dummy value of -64.6 °C. This 
    value will result in returning None unless debug mode is enabled.
    """

    # TODO verify
    # verified by G-nn-r: 0
    energy_state = enum_value(
        11, EnergyState, description="Smart-grid energy state currently in effect"
    )
    """Smart-grid energy state currently in effect."""

    # verified by G-nn-r: 9.4, 10.0, 15.5, 16.2, 16.5, 16.8, 17.2, 17.8, 18.1, 22.1, 22.4, 24.1
    outdoor_temperature = temperature(12, description="Outdoor air temperature")
    """Outdoor air temperature."""

    # TODO verify non-sentinel values
    water_pressure = hide_sentinel(
        gauge(
        13, description="Water pressure", scale=0.1, unit="BAR", signed=False,
        ),
        sentinel=NO_WATER_PRESSURE,
    )
    """
    Water pressure, only available for R290 units.
    """


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
    # Rescaled recently. Expected values are 25-65 °C for R32, G-nn-r reports 11-40 °C with compressor off; 28-55 °C with compressor running (increasing with compressor frequency)
    liquid_pipe_temperature = temperature(
        16, scale=0.1, digits=0, description="Refrigerant liquid pipe temperature"
    )
    """Refrigerant liquid pipe temperature."""

    # TODO verify
    # Rescaled recently. Expected values are -15 to +15 °C for R32, G-nn-r reports 8-30 °C without compressor running, 6-12 °C with compressor running
    suction_temperature = temperature(
        18, scale=0.1, digits=0, description="Compressor suction temperature"
    )
    """Compressor suction temperature."""

    # TODO verify
    # Rescaled recently. Expected values for CDT are 80-100°C (at max 65-110°C), G-nn-r reports 19-82
    # "R32's critical temperature is 78.1°C. Above this point, R32 cannot exist as a distinct liquid or vapor—it becomes a supercritical fluid, and the entire refrigeration cycle breaks down."
    # system could also be designed to work in supercritical range, this topic is a rabbit hole
    discharge_temperature = temperature(
        19, scale=0.1, digits=0, description="Compressor discharge temperature"
    )
    """Compressor discharge temperature."""
    # formerly hp_temp_heatgas "Heißgastemperatur"

    # TODO verify
    # Rescaled recently.
    # G-nn-r gets 10.0 to 25.7 °C (or without compressor running, 5.2-13.3 with compressor running (the higher the RPM, the lower the temperature), seems reasonable
    # expected values are between -5 °C and 15 °C in moderate climate, up to -25 °C at extreme cold (-10 °C ambient)
    # Was the rescaling really right? More analysis on which value is actually correct - this or evaporator_outlet_temperature  (a bit more likely)
    evaporator_inlet_temperature = temperature(
        20, scale=0.1, digits=0, description="Refrigerant temperature entering the evaporator"
    )
    """Evaporator inlet temperature."""

    # TODO verify
    # this is always equal to evaporator_inlet_temperature for G-nn-r, should only be the case when the compressor is off (otherwise an indication for no refrigerant flow or some other malfunction)
    # should be 5-15 K higher than evaporator_inlet_temperature and similar to suction_temperature, to be analyzed
    evaporator_outlet_temperature = temperature(
        21, scale=0.1, digits=0, description="Refrigerant temperature leaving the evaporator"
    )
    """Evaporator outlet temperature."""

    # TODO verify
    # G-nn-r gets values of roughly 10 to 14 bar when the compressor is off and roughly 18 to 25 bar when the compressor is on, values go up with compressor frequency, up to 37.75
    # expected are 20-35 bar for cold ambient, 35-50 bar for moderate ambient, 40-60 bar for DHW on warm days. Values should be below critical pressure (73.8 bar)
    # here mBar is mentioned, that would be too low: https://gathering.tweakers.net/forum/list_message/76531486#76531486
    # talk to basti242 about this, the list mentions °C: https://github.com/basti242/homeassistant_lg_therma_v_modbus/wiki/LG-Register-documentation
    refrigerant_high_pressure = gauge(
        22, 0.01, signed=False, unit=BAR, description="Condenser (high side) pressure"
    )
    """Condenser (high side) pressure."""

    # TODO verify
    # G-nn-r gets values of roughly 10.40 to 13.20 when the compressor is off and roughly 12 to 14 bar when the compressor is on (low speed: 9 or 11; higher speed: slightly increasing 8.8->9.7),
    # expected: 8-12 bar idle, 6-12 bar running
    # but the difference to refrigerant_high_pressure should be near-zero for compressor off, low for low compressor speed and high for high compressor speed, which is not the case for G-nn-r's readings
    # here mBar is mentioned, that would be too low: https://gathering.tweakers.net/forum/list_message/76531486#76531486
    # talk to basti242 about this, the list mentions °C: https://github.com/basti242/homeassistant_lg_therma_v_modbus/wiki/LG-Register-documentation
    refrigerant_low_pressure = gauge(
        23, 0.01, signed=False, unit=BAR, description="Evaporator (low side) pressure"
    )
    """Evaporator (low side) pressure."""

    # verified by G-nn-r: 0, 15, 27, 30, 34, 35, 37, 43, 45, 53, 54, 57, 60, 66. Maximum is expected at around ~50 Hz
    compressor_frequency = integer(
        24, signed=False, unit=HERTZ, description="Compressor rotation frequency"
    )
    """Compressor rotation frequency, in revolutions per second."""

    # verified by G-nn-r, deriving works as expected
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

    @property
    def water_temperature_drop_circuit_2(self) -> float | None:
        """Return the temperature drop from circuit 1 to the mixed circuit 2 outlet."""
        outlet = self.water_outlet_temperature
        mixed = self.water_outlet_temperature_circuit_2
        if outlet is None or mixed is None:
            return None
        return round(outlet - mixed, 1)
