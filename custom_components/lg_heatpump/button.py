"""Button platform for the LG Heat Pump integration."""

from typing import override

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LgHeatPumpConfigEntry, LgHeatPumpRuntimeData

PARALLEL_UPDATES = 1

REFRESH_DESCRIPTION = ButtonEntityDescription(
    key="refresh",
    translation_key="refresh",
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LgHeatPumpConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the LG heat pump button platform."""
    async_add_entities([LgHeatPumpRefreshButton(entry.runtime_data, entry.entry_id)])


class LgHeatPumpRefreshButton(ButtonEntity):
    """Polls the measurements and the settings right away."""

    _attr_has_entity_name = True

    def __init__(self, runtime_data: LgHeatPumpRuntimeData, entry_id: str) -> None:
        """Initialize the button."""
        self.entity_description = REFRESH_DESCRIPTION
        self._runtime_data = runtime_data
        self._attr_unique_id = f"{entry_id}_{REFRESH_DESCRIPTION.key}"
        self._attr_device_info = runtime_data.readings.device_info

    @override
    async def async_press(self) -> None:
        """Poll both tables now, skipping the coordinators' request debounce."""
        # One after the other, to keep the load on the Modbus link low.
        await self._runtime_data.readings.async_refresh()
        await self._runtime_data.settings.async_refresh()
