"""On/off commands the controller accepts (coils, FC01/FC05)."""

from __future__ import annotations

from ..data_model import LgComponent, coil


class Switches(LgComponent):
    """The four writable coils: heating circuit, hot water, silent mode and disinfection."""

    coil_ranges = ((0, 3),)

    # verified by G-nn-r: off/False/0 and on/True/1, switching in both directions
    # formerly hp_hauptschalter
    # TODO create conversion table for all (entity) names that have changed
    heating_circuit = coil(
        0, writable=True, description="Hydronic circuit for space heating and cooling enabled"
    )
    """
    Whether the hydronic circuit for space heating and cooling is enabled. Can be controlled via set_heating_circuit().
    
    The actual mode (heating/cooling/auto) is available in Controls.operation_mode and set via set_operation_mode().

    heating_circuit does not affect domestic hot water (DHW) production, this is controlled by dhw.
    """

    # verified by G-nn-r: off/False/0 and on/True/1, switching in both directions
    dhw = coil(1, writable=True, description="Domestic hot water production on/off")
    """
    Whether domestic hot water (DHW) production is enabled.
    Can be controlled via set_dhw()
    """

    # verified by G-nn-r: off/False/0 and on/True/1, switching in both directions
    silent_mode = coil(2, writable=True, description="Silent (night) mode on/off")
    """
    Whether silent mode is enabled.
    Can be controlled via set_silent_mode()
    """

    # TODO verify
    # verified by G-nn-r: off/False/0 and on/True/1, and switching on. Switching off did not work - intended behavior to complete disinfection cycle?
    dhw_disinfection = coil(
        3, writable=True, description="Domestic hot water disinfection cycle on/off"
    )
    """
    Whether the hot water disinfection cycle is enabled.
    Can be controlled via set_dhw_disinfection()
    """

    async def set_heating_circuit(self, value: bool) -> None:
        """Enable or disable the hydronic circuit for space heating and cooling."""
        await self.write("heating_circuit", value)

    async def set_dhw(self, value: bool) -> None:
        """Enable or disable domestic hot water production."""
        await self.write("dhw", value)

    async def set_silent_mode(self, value: bool) -> None:
        """Enable or disable silent mode."""
        await self.write("silent_mode", value)

    async def set_dhw_disinfection(self, value: bool) -> None:
        """Enable or disable the hot water disinfection cycle."""
        await self.write("dhw_disinfection", value)
