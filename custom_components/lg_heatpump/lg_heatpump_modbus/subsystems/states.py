"""Running state the heat pump reports (discrete inputs, FC02, read-only)."""

from __future__ import annotations

from ..data_model import LgComponent, discrete_input


class States(LgComponent):
    """Pump, heater, compressor and fault flags, read in one block."""

    discrete_ranges = ((0, 16),)

    water_flow = discrete_input(0, description="Water flow detected")
    """Whether water flow is detected."""

    water_pump = discrete_input(1, description="Internal water pump running")
    """Whether the internal water pump is running."""

    external_water_pump = discrete_input(2, description="External water pump running")
    """Whether the external water pump is running."""

    compressor = discrete_input(3, description="Compressor running")
    """Whether the compressor is running."""

    defrosting = discrete_input(4, description="Defrost cycle active")
    """Whether a defrost cycle is active."""

    dhw_heating = discrete_input(5, description="Heating domestic hot water")
    """Whether domestic hot water is being heated."""

    dhw_disinfection = discrete_input(
        6, description="Domestic hot water disinfection cycle running"
    )
    """Whether the hot water disinfection cycle is running."""

    silent_mode = discrete_input(7, description="Silent mode active")
    """Whether silent mode is active."""

    cooling = discrete_input(8, description="Cooling")
    """Whether the heat pump is cooling."""

    solar_pump = discrete_input(9, description="Solar pump running")
    """Whether the solar pump is running."""

    backup_heater_step_1 = discrete_input(10, description="Backup heater step 1 on")
    """Whether backup heater step 1 is on."""

    backup_heater_step_2 = discrete_input(11, description="Backup heater step 2 on")
    """Whether backup heater step 2 is on."""

    dhw_boost_heater = discrete_input(
        12, description="Domestic hot water boost heater on"
    )
    """Whether the hot water boost heater is on."""

    error = discrete_input(13, description="An error is active")
    """Whether an error is active."""

    emergency_operation_space = discrete_input(
        14, description="Emergency operation available for space heating/cooling"
    )
    """Whether emergency operation is available for space heating/cooling."""

    emergency_operation_dhw = discrete_input(
        15, description="Emergency operation available for domestic hot water"
    )
    """Whether emergency operation is available for domestic hot water."""

    mixing_pump = discrete_input(16, description="Mixing pump running")
    """Whether the mixing pump is running."""

    @property
    def backup_heater_steps(self) -> int | None:
        """Return how many backup heater steps are on, or ``None`` if unread."""
        steps = (self.backup_heater_step_1, self.backup_heater_step_2)
        if any(step is None for step in steps):
            return None
        return sum(1 for step in steps if step)
