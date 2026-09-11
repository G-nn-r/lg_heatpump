"""Device models: which datapoints a heat pump variant actually serves.

A variant is added here as **data**, never as code. A :class:`ModelDefinition`
names the optional features an installation has; the feature groups below map
those features onto the datapoints they enable. Everything a model does not
have is excluded from the read plan, so a heat pump without a second circuit
never issues a read for it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

#: Datapoints that only exist when the installation has a second water circuit.
CIRCUIT_2_DATAPOINTS: frozenset[str] = frozenset(
    {
        "water_outlet_temperature_circuit_2",
        "room_air_temperature_circuit_2",
        "target_temperature_circuit_2",
        "room_air_setpoint_circuit_2",
        "shift_in_auto_mode_circuit_2",
    }
)

#: Datapoints that only exist when a domestic hot water tank is fitted.
DHW_DATAPOINTS: frozenset[str] = frozenset(
    {
        "dhw_tank_temperature",
        "dhw_target_temperature",
        "dhw",
        "dhw_disinfection",
        "dhw_heating",
        "dhw_boost_heater",
        "emergency_operation_dhw",
    }
)

#: Datapoints that only exist when a solar collector is connected.
SOLAR_DATAPOINTS: frozenset[str] = frozenset(
    {"solar_collector_temperature", "solar_pump"}
)

#: Datapoints that only exist when a mixing valve/pump is fitted.
MIXING_DATAPOINTS: frozenset[str] = frozenset({"mixing_pump"})

#: Datapoints that only exist when a backup (electric) heater is fitted.
BACKUP_HEATER_DATAPOINTS: frozenset[str] = frozenset(
    {
        "backup_heater_outlet_temperature",
        "backup_heater_step_1",
        "backup_heater_step_2",
    }
)

#: Refrigerant-circuit diagnostics, absent on units that do not publish them.
REFRIGERANT_DATAPOINTS: frozenset[str] = frozenset(
    {
        "liquid_pipe_temperature",
        "suction_temperature",
        "discharge_temperature",
        "evaporator_inlet_temperature",
        "evaporator_outlet_temperature",
        "high_pressure",
        "low_pressure",
        "compressor_frequency",
    }
)


@dataclass(frozen=True)
class ModelDefinition:
    """One heat pump variant, described by the optional features it has."""

    key: str
    """Stable identifier, safe to persist in a configuration."""

    name: str
    """Human-readable model name."""

    circuits: int = 2
    """Number of water circuits, 1 or 2."""

    has_dhw: bool = True
    """Whether a domestic hot water tank is fitted."""

    has_solar: bool = False
    """Whether a solar collector is connected."""

    has_mixing_valve: bool = True
    """Whether a mixing valve/pump is fitted."""

    has_backup_heater: bool = True
    """Whether an electric backup heater is fitted."""

    has_refrigerant_diagnostics: bool = True
    """Whether the unit publishes refrigerant-circuit diagnostics."""

    aliases: tuple[str, ...] = field(default_factory=tuple)
    """Other marketing names that share this register map."""

    def __post_init__(self) -> None:
        """Reject a model that claims a number of circuits that cannot exist."""
        if self.circuits not in (1, 2):
            raise ValueError(f"A model has 1 or 2 circuits, not {self.circuits}")

    @property
    def excluded_datapoints(self) -> frozenset[str]:
        """Return every datapoint this model does not serve."""
        excluded: frozenset[str] = frozenset()
        if self.circuits < 2:
            excluded |= CIRCUIT_2_DATAPOINTS
        if not self.has_dhw:
            excluded |= DHW_DATAPOINTS
        if not self.has_solar:
            excluded |= SOLAR_DATAPOINTS
        if not self.has_mixing_valve:
            excluded |= MIXING_DATAPOINTS
        if not self.has_backup_heater:
            excluded |= BACKUP_HEATER_DATAPOINTS
        if not self.has_refrigerant_diagnostics:
            excluded |= REFRIGERANT_DATAPOINTS
        return excluded

    def serves(self, datapoint: str) -> bool:
        """Return whether this model serves ``datapoint``."""
        return datapoint not in self.excluded_datapoints

    def supported(self, datapoints: object) -> tuple[str, ...]:
        """Return the members of ``datapoints`` this model serves, in order."""
        return tuple(name for name in datapoints if self.serves(name))  # type: ignore[union-attr]


#: The full Therma V register map: everything the validated map documents.
THERMA_V = ModelDefinition(
    key="therma_v",
    name="LG Therma V",
    has_solar=True,
    aliases=("Therma V Monobloc", "Therma V Split", "Therma V R32"),
)

#: A single-circuit installation without solar or a mixing valve.
THERMA_V_SINGLE_CIRCUIT = ModelDefinition(
    key="therma_v_single_circuit",
    name="LG Therma V (single circuit)",
    circuits=1,
    has_solar=False,
    has_mixing_valve=False,
)

#: A space-heating-only installation: no hot water tank.
THERMA_V_HEATING_ONLY = ModelDefinition(
    key="therma_v_heating_only",
    name="LG Therma V (heating only)",
    has_dhw=False,
    has_solar=True,
)

#: Every model this library knows, keyed by :attr:`ModelDefinition.key`.
MODELS: Mapping[str, ModelDefinition] = MappingProxyType(
    {
        model.key: model
        for model in (THERMA_V, THERMA_V_SINGLE_CIRCUIT, THERMA_V_HEATING_ONLY)
    }
)

#: The model assumed when a caller does not name one.
DEFAULT_MODEL = THERMA_V


def get_model(key: str) -> ModelDefinition:
    """Return the model definition registered under ``key``."""
    try:
        return MODELS[key]
    except KeyError:
        known = ", ".join(sorted(MODELS))
        raise ValueError(f"Unknown model {key!r}; known models: {known}") from None
