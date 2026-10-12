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
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LgHeatPumpConfigEntry, LgHeatPumpCoordinator
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
    _state("backup_heater_step_1", BinarySensorDeviceClass.RUNNING, enabled=False),
    _state("backup_heater_step_2", BinarySensorDeviceClass.RUNNING, enabled=False),
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
    runtime_data = entry.runtime_data
    async_add_entities(
        build_entities(
            runtime_data,
            LgHeatPumpBinarySensor,
            BINARY_SENSOR_DESCRIPTIONS,
        )
    )
    async_add_entities(
        [
            LgHeatPumpUpdateProblemSensor(
                runtime_data.readings,
                translation_key="readings_update_problem",
            ),
            LgHeatPumpUpdateProblemSensor(
                runtime_data.settings,
                translation_key="settings_update_problem",
            ),
        ]
    )


class LgHeatPumpBinarySensor(LgHeatPumpEntity, BinarySensorEntity):
    """A single discrete input read from the heat pump."""

    entity_description: LgHeatPumpBinarySensorDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """Return whether the discrete input is set."""
        return self._value


class LgHeatPumpUpdateProblemSensor(
    CoordinatorEntity[LgHeatPumpCoordinator], BinarySensorEntity
):
    """Debug sensor: on while a coordinator's last poll failed, even partly.

    Unlike the other entities it stays available when the poll fails, because
    reporting exactly that failure is its purpose.
    """

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: LgHeatPumpCoordinator,
        translation_key: str,
    ) -> None:
        """Initialize the sensor for one coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{translation_key}"
        self._attr_device_info = coordinator.device_info

    @property
    @override
    def available(self) -> bool:
        """Stay available so a failed poll can be reported."""
        return True

    @property
    @override
    def is_on(self) -> bool:
        """Return whether the last poll failed completely or in part."""
        return not self.coordinator.last_update_success or bool(
            self.coordinator.data.failed
        )

    @property
    @override
    def extra_state_attributes(self) -> dict[str, list[str]]:
        """Return the sub-systems that did not answer the last poll."""
        if not self.coordinator.last_update_success:
            return {}
        return {"failed_components": sorted(self.coordinator.data.failed)}
