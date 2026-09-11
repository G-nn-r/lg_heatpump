"""Neutral datapoint metadata carried alongside the register declarations.

The metadata is deliberately framework-agnostic: it describes *what a value is*
(range, step, unit, options, whether it can be written), not how any particular
application should present it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Literal

ValueKind = Literal["number", "enum", "boolean", "raw"]


@dataclass(frozen=True)
class NumberMetadata:
    """Metadata for numeric values."""

    min_value: float | int | None = None
    max_value: float | int | None = None
    step: float | int | None = None
    digits: int | None = None
    unit: str | None = None


@dataclass(frozen=True)
class OptionMetadata:
    """Metadata for one discrete option of an enumerated value."""

    key: str
    value: int
    description: str | None = None


@dataclass(frozen=True)
class EnumMetadata:
    """Metadata for selectable / discrete register values."""

    enum_type: type[IntEnum]
    options: tuple[OptionMetadata, ...]


@dataclass(frozen=True)
class BooleanMetadata:
    """Metadata for boolean coil and discrete-input values."""

    false_key: str = "off"
    true_key: str = "on"


RegisterType = Literal["input", "holding", "coil", "discrete"]


@dataclass(frozen=True)
class DatapointMetadata:
    """Neutral metadata for one heat pump datapoint.

    ``register_type`` and ``address`` describe where the value lives. They are
    left unset on the field declaration and filled in by
    :meth:`~lg_heatpump_modbus.data_model.LgComponent.metadata_for`, which is
    the only place that knows the component's register space and the absolute
    address the value ended up at.
    """

    value_kind: ValueKind
    description: str | None = None
    writable: bool = False
    register_type: RegisterType | None = None
    address: int | None = None
    number: NumberMetadata | None = None
    enum: EnumMetadata | None = None
    boolean: BooleanMetadata | None = None


def step_from_digits(digits: int | None) -> float | int | None:
    """Return the natural UI/write step implied by a decimal precision."""
    if digits is None:
        return None
    if digits <= 0:
        return 1
    return 10**-digits


def options_from_enum(enum_type: type[IntEnum]) -> tuple[OptionMetadata, ...]:
    """Return the option metadata for every member of an ``IntEnum``."""
    return tuple(
        OptionMetadata(
            key=member.name.lower(),
            value=int(member),
            description=(
                member.__doc__ if member.__doc__ != enum_type.__doc__ else None
            ),
        )
        for member in enum_type
    )


def attach_metadata(field: Any, metadata: DatapointMetadata) -> Any:
    """Attach heat pump metadata to a ``modbus-connection`` field object."""
    field.lg_metadata = metadata
    return field
