"""Switch platform for the LG Heat Pump integration."""

from dataclasses import dataclass
from typing import Any, override

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LgHeatPumpConfigEntry
from .entity import LgHeatPumpEntity, LgHeatPumpEntityDescription, build_entities

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class LgHeatPumpSwitchDescription(SwitchEntityDescription, LgHeatPumpEntityDescription):
    """Describe an LG heat pump switch."""


SWITCH_DESCRIPTIONS: tuple[LgHeatPumpSwitchDescription, ...] = (
    LgHeatPumpSwitchDescription(
        key="power",
        translation_key="power",
        component="switches",
        attribute="power",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    LgHeatPumpSwitchDescription(
        key="dhw",
        translation_key="dhw",
        component="switches",
        attribute="dhw",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    LgHeatPumpSwitchDescription(
        key="silent_mode",
        translation_key="silent_mode",
        component="switches",
        attribute="silent_mode",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    LgHeatPumpSwitchDescription(
        key="dhw_disinfection",
        translation_key="dhw_disinfection",
        component="switches",
        attribute="dhw_disinfection",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LgHeatPumpConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the LG heat pump switch platform."""
    async_add_entities(
        build_entities(entry.runtime_data, LgHeatPumpSwitch, SWITCH_DESCRIPTIONS)
    )


class LgHeatPumpSwitch(LgHeatPumpEntity, SwitchEntity):
    """A single writable coil on the heat pump."""

    entity_description: LgHeatPumpSwitchDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return whether the coil is set."""
        return self._value

    async def _async_write(self, value: bool) -> None:
        """Write the coil and refresh so the state follows the device."""
        await self._subsystem.write(self.entity_description.attribute, value)
        await self.coordinator.async_request_refresh()

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Set the coil."""
        await self._async_write(True)

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Clear the coil."""
        await self._async_write(False)
