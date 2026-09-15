"""Running state the heat pump reports (discrete inputs, FC02, read-only)."""

from __future__ import annotations

from ..data_model import LgComponent, discrete_input


class States(LgComponent):
    """Pump, heater, compressor and fault flags, read in one block."""

    discrete_ranges = ((0, 16),)

    # TODO verify
    # verified by G-nn-r: so far only on/True/1
    water_flow = discrete_input(0, description="Water flow detected")
    """Whether water flow is detected."""

    # TODO verify
    # verified by G-nn-r: so far only on/True/1
    water_pump = discrete_input(1, description="Internal water pump running")
    """Whether the internal water pump is running."""

    # TODO verify
    # verified by G-nn-r: so far only on/True/1
    external_water_pump = discrete_input(2, description="External water pump running")
    """Whether the external water pump is running."""

    # verified by G-nn-r: off/False/0 and on/True/1
    compressor = discrete_input(3, description="Compressor running")
    """Whether the compressor is running."""

    # TODO verify
    # verified by G-nn-r: so far only off/False/0
    defrosting = discrete_input(4, description="Defrost cycle active")
    """Whether a defrost cycle is active."""

    # TODO verify
    # verified by G-nn-r: so far only off/False/0
    dhw_heating = discrete_input(5, description="Heating domestic hot water")
    """Whether domestic hot water (DHW) is being heated."""

    # TODO verify
    # verified by G-nn-r: so far only off/False/0, this can be triggered from HA or via time schedule (Fridays 3pm?)
    dhw_disinfection = discrete_input(
        6, description="Domestic hot water disinfection cycle running"
    )
    """Whether the hot water disinfection cycle is running."""

    # verified by G-nn-r: off/False/0 and on/True/1
    silent_mode = discrete_input(7, description="Silent mode active")
    """Whether silent mode is active."""

    # TODO verify
    # G-nn-r: so far only gotten on/True/1, despite it was in auto/AI mode, --> check behavior in explicit heating mode
    cooling = discrete_input(8, description="Cooling")
    """Whether the heat pump is cooling."""

    # TODO verify
    # verified by G-nn-r: so far only off/False/0
    solar_pump = discrete_input(9, description="Solar pump running")
    """Whether the solar pump is running."""
    # TODO is this about running or presence?

    # TODO verify
    # verified by G-nn-r: so far only off/False/0, this might be triggerable with DHW > 52°C
    backup_heater_step_1 = discrete_input(10, description="Backup heater step 1 on")
    """Whether backup heater step 1 is on."""

    # TODO verify
    # verified by G-nn-r: so far only off/False/0, this might be triggerable with DHW > 52°C
    backup_heater_step_2 = discrete_input(11, description="Backup heater step 2 on")
    """Whether backup heater step 2 is on."""

    # TODO verify
    # verified by G-nn-r: so far only off/False/0, this might be triggerable with DHW > 52°C
    dhw_boost_heater = discrete_input(
        12, description="Domestic hot water boost heater on"
    )
    """Whether the hot water boost heater is on."""
    # TODO adjust docstring: Is this really saying its on or just requesting it to be on?

    # TODO verify
    # verified by G-nn-r: so far only off/False/0
    error = discrete_input(13, description="An error is active")
    """Whether an error is active."""

    # TODO verify
    # verified by G-nn-r: so far only off/False/0, do some research what this actually means and how to trigger it
    emergency_operation_space = discrete_input(
        14, description="Emergency operation available for space heating/cooling"
    )
    """Whether emergency operation is available for space heating/cooling."""

    # TODO verify
    # verified by G-nn-r: so far only off/False/0, do some research what this actually means and how to trigger it
    emergency_operation_dhw = discrete_input(
        15, description="Emergency operation available for domestic hot water"
    )
    """Whether emergency operation is available for domestic hot water."""

    # TODO verify
    # verified by G-nn-r: so far always on/True/1 but so far only tested with power=True. Is this about running or just presence?
    mixing_pump = discrete_input(16, description="Mixing pump running")
    """Whether the mixing pump is running."""

    # TODO is this needed? Depending on the actual meaning of the steps, this might needs to be thought out again
    @property
    def backup_heater_steps(self) -> int | None:
        """Return how many backup heater steps are on, or ``None`` if unread."""
        steps = (self.backup_heater_step_1, self.backup_heater_step_2)
        if any(step is None for step in steps):
            return None
        return sum(1 for step in steps if step)
