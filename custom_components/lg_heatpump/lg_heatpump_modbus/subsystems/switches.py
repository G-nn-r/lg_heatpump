"""On/off commands the controller accepts (coils, FC01/FC05)."""

from __future__ import annotations

from ..data_model import LgComponent, coil


class Switches(LgComponent):
    """The four writable coils: power, hot water, silent mode and disinfection."""

    coil_ranges = ((0, 3),)

    # TODO verify
    # verified by G-nn-r: off/False/0 and on/True/1. Switching was verified only turning on (->True, -> 1)
    # TODO decide whether refactoring should be applied to avoid confusion with power in watts
    # formerly hp_hauptschalter
    # TODO create conversion table for all (entity) names that have changed
    power = coil(0, writable=True, description="Heat pump on/off")
    """
    Whether the heat pump is switched on.
    Can be controlled via set_power()
    """

    # verified by G-nn-r: on/True/1 and off/False/0
    dhw = coil(1, writable=True, description="Domestic hot water production on/off")
    """
    Whether domestic hot water (DHW) production is enabled.
    Can be controlled via set_dhw()
    """

    # verified by G-nn-r: off/False/0 and on/True/1
    silent_mode = coil(2, writable=True, description="Silent (night) mode on/off")
    """
    Whether silent mode is enabled.
    Can be controlled via set_silent_mode()
    """

    # TODO verify
    # verified by G-nn-r: off/False/0
    dhw_disinfection = coil(
        3, writable=True, description="Domestic hot water disinfection cycle on/off"
    )
    """
    Whether the hot water disinfection cycle is enabled.
    Can be controlled via set_dhw_disinfection()
    """

    async def set_power(self, value: bool) -> None:
        """Switch the heat pump on or off."""
        await self.write("power", value)

    async def set_dhw(self, value: bool) -> None:
        """Enable or disable domestic hot water production."""
        await self.write("dhw", value)

    async def set_silent_mode(self, value: bool) -> None:
        """Enable or disable silent mode."""
        await self.write("silent_mode", value)

    async def set_dhw_disinfection(self, value: bool) -> None:
        """Enable or disable the hot water disinfection cycle."""
        await self.write("dhw_disinfection", value)
