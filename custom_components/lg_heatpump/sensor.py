"""Sensor platform for the LG Heat Pump integration."""

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import override

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LgHeatPumpConfigEntry, LgHeatPumpCoordinator
from .entity import LgHeatPumpEntity, LgHeatPumpEntityDescription, build_entities
from .lg_heatpump_modbus import EnergyState, OduOperationCycle

PARALLEL_UPDATES = 0

_ENERGY_STATE_OPTIONS = [state.name.lower() for state in EnergyState]
_ODU_OPERATION_CYCLE_OPTIONS = [state.name.lower() for state in OduOperationCycle]


@dataclass(frozen=True, kw_only=True)
class LgHeatPumpSensorDescription(SensorEntityDescription, LgHeatPumpEntityDescription):
    """Describe an LG heat pump sensor."""


def _temperature(
    attribute: str,
    *,
    component: str = "sensors",
    enabled: bool = True,
    diagnostic: bool = True,
) -> LgHeatPumpSensorDescription:
    """Describe a temperature reading."""
    return LgHeatPumpSensorDescription(
        key=attribute,
        translation_key=attribute,
        component=component,
        attribute=attribute,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC if diagnostic else None,
        entity_registry_enabled_default=enabled,
    )


def _pressure(attribute: str) -> LgHeatPumpSensorDescription:
    """Describe a pressure reading."""
    return LgHeatPumpSensorDescription(
        key=attribute,
        translation_key=attribute,
        component="sensors",
        attribute=attribute,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    )


SENSOR_DESCRIPTIONS: tuple[LgHeatPumpSensorDescription, ...] = (
    _temperature("outdoor_temperature", diagnostic=False),
    _temperature("water_inlet_temperature", diagnostic=False),
    _temperature("water_outlet_temperature", diagnostic=False),
    _temperature("dhw_tank_temperature", diagnostic=False),
    _temperature("room_air_temperature_circuit_1"),
    _temperature("room_air_temperature_circuit_2"),
    _temperature("water_outlet_temperature_circuit_2"),
    _temperature("backup_heater_outlet_temperature", enabled=False),
    _temperature("solar_collector_temperature", enabled=False),
    _temperature("liquid_pipe_temperature", enabled=False),
    _temperature("suction_temperature", enabled=False),
    _temperature("discharge_temperature", enabled=False),
    _temperature("evaporator_inlet_temperature", enabled=False),
    _temperature("evaporator_outlet_temperature", enabled=False),
    _pressure("refrigerant_high_pressure"),
    _pressure("refrigerant_low_pressure"),
    _pressure("water_pressure"),
    LgHeatPumpSensorDescription(
        key="water_flow_rate",
        translation_key="water_flow_rate",
        component="sensors",
        attribute="water_flow_rate",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    LgHeatPumpSensorDescription(
        key="compressor_speed",
        translation_key="compressor_speed",
        component="sensors",
        attribute="compressor_frequency",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    LgHeatPumpSensorDescription(
        key="error_code",
        translation_key="error_code",
        component="sensors",
        attribute="error_code",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    LgHeatPumpSensorDescription(
        key="odu_operation_cycle",
        translation_key="odu_operation_cycle",
        component="sensors",
        attribute="odu_operation_cycle",
        device_class=SensorDeviceClass.ENUM,
        options=_ODU_OPERATION_CYCLE_OPTIONS,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    LgHeatPumpSensorDescription(
        key="energy_state",
        translation_key="energy_state",
        component="sensors",
        attribute="energy_state",
        device_class=SensorDeviceClass.ENUM,
        options=_ENERGY_STATE_OPTIONS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

# Sensors whose value the library derives from several registers.
DERIVED_DESCRIPTIONS: tuple[LgHeatPumpSensorDescription, ...] = (
    LgHeatPumpSensorDescription(
        key="water_outlet_temperature_circuit_1",
        translation_key="water_outlet_temperature_circuit_1",
        component="sensors",
        attribute="water_outlet_temperature_circuit_1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    LgHeatPumpSensorDescription(
        key="water_temperature_difference",
        translation_key="water_temperature_difference",
        component="sensors",
        attribute="water_temperature_difference",
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    LgHeatPumpSensorDescription(
        key="water_temperature_drop_circuit_2",
        translation_key="water_temperature_drop_circuit_2",
        component="sensors",
        attribute="water_temperature_drop_circuit_2",
        native_unit_of_measurement=UnitOfTemperature.KELVIN,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LgHeatPumpConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the LG heat pump sensor platform."""
    runtime_data = entry.runtime_data
    entities: list[SensorEntity] = [
        *build_entities(runtime_data, LgHeatPumpSensor, SENSOR_DESCRIPTIONS),
        *(
            LgHeatPumpSensor(runtime_data, description)
            for description in DERIVED_DESCRIPTIONS
        ),
    ]
    entities += [
        LgHeatPumpLastPollSensor(
            runtime_data.readings,
            translation_key="readings_last_poll",
        ),
        LgHeatPumpLastPollSensor(
            runtime_data.settings,
            translation_key="settings_last_poll",
        ),
    ]
    async_add_entities(entities)


class LgHeatPumpLastPollSensor(CoordinatorEntity[LgHeatPumpCoordinator], SensorEntity):
    """Debug sensor: when a coordinator last polled, successful or not.

    It stays available when the poll fails, so a stalled poll shows up as a
    timestamp that stops advancing.
    """

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP
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
    def native_value(self) -> datetime | None:
        """Return when the last poll finished."""
        return self.coordinator.last_poll_time


class LgHeatPumpSensor(LgHeatPumpEntity, SensorEntity):
    """A single value read from a heat pump sub-system."""

    entity_description: LgHeatPumpSensorDescription

    @property
    @override
    def native_value(self) -> str | int | float | None:
        """Return the current value, mapping enums onto their option slug."""
        value = self._value
        if isinstance(value, IntEnum):
            return value.name.lower()
        if self.entity_description.key == "compressor_speed":
            return self._subsystem.compressor_speed
        return value
