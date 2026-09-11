"""Binary sensor platform for the LG Heat Pump integration."""

from dataclasses import dataclass
from typing import override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LgHeatPumpConfigEntry
from .entity import LgHeatPumpEntity, LgHeatPumpEntityDescription, build_entities

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class LgHeatPumpBinarySensorDescription(
    BinarySensorEntityDescription, LgHeatPumpEntityDescription
):
    """Describe an LG heat pump binary sensor."""


def _state(
    attribute: str,
    device_class: BinarySensorDeviceClass | None = None,
    *,
    enabled: bool = True,
) -> LgHeatPumpBinarySensorDescription:
    """Describe a discrete input reported by the heat pump."""
    return LgHeatPumpBinarySensorDescription(
        key=attribute,
        translation_key=attribute,
        component="states",
        attribute=attribute,
        device_class=device_class,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=enabled,
    )


BINARY_SENSOR_DESCRIPTIONS: tuple[LgHeatPumpBinarySensorDescription, ...] = (
    _state("error", BinarySensorDeviceClass.PROBLEM),
    _state("compressor", BinarySensorDeviceClass.RUNNING),
    _state("water_pump", BinarySensorDeviceClass.RUNNING),
    _state("external_water_pump", BinarySensorDeviceClass.RUNNING, enabled=False),
    _state("mixing_pump", BinarySensorDeviceClass.RUNNING, enabled=False),
    _state("solar_pump", BinarySensorDeviceClass.RUNNING, enabled=False),
    _state("water_flow", BinarySensorDeviceClass.RUNNING),
    _state("defrosting", BinarySensorDeviceClass.RUNNING),
    _state("cooling", BinarySensorDeviceClass.COLD),
    _state("dhw_heating", BinarySensorDeviceClass.HEAT),
    _state("dhw_disinfection", BinarySensorDeviceClass.RUNNING, enabled=False),
    _state("dhw_boost_heater", BinarySensorDeviceClass.HEAT, enabled=False),
    _state("backup_heater_step_1", BinarySensorDeviceClass.HEAT),
    _state("backup_heater_step_2", BinarySensorDeviceClass.HEAT, enabled=False),
    _state("silent_mode", BinarySensorDeviceClass.RUNNING),
    _state("emergency_operation_space", enabled=False),
    _state("emergency_operation_dhw", enabled=False),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LgHeatPumpConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the LG heat pump binary sensor platform."""
    async_add_entities(
        build_entities(
            entry.runtime_data,
            LgHeatPumpBinarySensor,
            BINARY_SENSOR_DESCRIPTIONS,
        )
    )


class LgHeatPumpBinarySensor(LgHeatPumpEntity, BinarySensorEntity):
    """A single discrete input read from the heat pump."""

    entity_description: LgHeatPumpBinarySensorDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return whether the discrete input is set."""
        return self._value
