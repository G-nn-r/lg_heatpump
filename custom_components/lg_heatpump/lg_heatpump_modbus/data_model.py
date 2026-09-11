"""LG-specific pieces layered on the ``modbus_connection.model`` framework.

The helpers here are thin wrappers around the framework's field helpers. They
add two things the framework deliberately leaves to a device library:

* **neutral metadata** — range, step, precision, unit, enum options and
  writability, recorded next to the address so the model *is* the datasheet;
* **write validation** — a value outside the documented range is rejected
  before it reaches the wire.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import replace
from enum import IntEnum
from typing import Any

from modbus_connection.model import (
    CoilField,
    Component,
    DiscreteInputField,
    RegisterField,
    coil as _coil,
    discrete_input as _discrete_input,
    enum as _enum,
    gauge as _gauge,
    integer as _integer,
    raw_register as _raw_register,
)

from .exceptions import LgValueValidationError
from .metadata import (
    BooleanMetadata,
    DatapointMetadata,
    EnumMetadata,
    NumberMetadata,
    attach_metadata,
    options_from_enum,
    step_from_digits,
)

CELSIUS = "°C"
BAR = "bar"
LITRES_PER_MINUTE = "L/min"
HERTZ = "Hz"

AnyField = RegisterField[Any] | CoilField | DiscreteInputField


def _number_validator(
    *,
    min_value: float | int | None,
    max_value: float | int | None,
) -> Callable[[Any], Any]:
    """Return a write validator rejecting values outside the documented range."""

    def validate(value: Any) -> Any:
        try:
            number = float(value)
        except (TypeError, ValueError) as err:
            raise LgValueValidationError(f"Value {value!r} is not a number") from err
        if min_value is not None and number < min_value:
            raise LgValueValidationError(
                f"Value {value} is below the minimum of {min_value}"
            )
        if max_value is not None and number > max_value:
            raise LgValueValidationError(
                f"Value {value} is above the maximum of {max_value}"
            )
        return value

    return validate


def _writable(
    writable: bool,
    *,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
) -> bool | Callable[[Any], Any]:
    """Return the ``writable`` argument the framework field should be given."""
    if not writable:
        return False
    if min_value is None and max_value is None:
        return True
    return _number_validator(min_value=min_value, max_value=max_value)


def _number_metadata(
    *,
    min_value: float | int | None,
    max_value: float | int | None,
    step: float | int | None,
    digits: int | None,
    unit: str | None,
) -> NumberMetadata:
    """Build the numeric metadata block, deriving the step from the precision."""
    return NumberMetadata(
        min_value=min_value,
        max_value=max_value,
        step=step if step is not None else step_from_digits(digits),
        digits=digits,
        unit=unit,
    )


def gauge(
    address: int,
    scale: float,
    *,
    signed: bool = True,
    unit: str | None = None,
    digits: int | None = None,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    step: float | int | None = None,
    writable: bool = False,
    description: str | None = None,
) -> RegisterField[float]:
    """Declare a scaled numeric register."""
    field = _gauge(
        address,
        scale,
        signed=signed,
        unit=unit,
        writable=_writable(writable, min_value=min_value, max_value=max_value),
    )
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            description=description,
            writable=writable,
            number=_number_metadata(
                min_value=min_value,
                max_value=max_value,
                step=step,
                digits=digits,
                unit=unit,
            ),
        ),
    )


def temperature(
    address: int,
    *,
    scale: float = 0.1,
    digits: int = 1,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    writable: bool = False,
    description: str | None = None,
) -> RegisterField[float]:
    """Declare a signed temperature register in degrees Celsius."""
    return gauge(
        address,
        scale,
        signed=True,
        unit=CELSIUS,
        digits=digits,
        min_value=min_value,
        max_value=max_value,
        writable=writable,
        description=description,
    )


def integer(
    address: int,
    *,
    signed: bool = True,
    unit: str | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
    writable: bool = False,
    description: str | None = None,
) -> RegisterField[int]:
    """Declare an unscaled integer register."""
    field = _integer(
        address,
        signed=signed,
        unit=unit,
        writable=_writable(writable, min_value=min_value, max_value=max_value),
    )
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            description=description,
            writable=writable,
            number=_number_metadata(
                min_value=min_value,
                max_value=max_value,
                step=1,
                digits=0,
                unit=unit,
            ),
        ),
    )


def raw_register(
    address: int,
    *,
    description: str | None = None,
) -> RegisterField[int]:
    """Declare a raw, uninterpreted register word."""
    field = _raw_register(address)
    return attach_metadata(
        field,
        DatapointMetadata(value_kind="raw", description=description),
    )


def enum_value[E: IntEnum](
    address: int,
    enum_type: type[E],
    *,
    writable: bool = False,
    description: str | None = None,
) -> RegisterField[E]:
    """Declare a register whose value maps onto an ``IntEnum``."""
    validator: bool | Callable[[Any], Any] = False
    if writable:

        def validate(value: Any) -> int:
            try:
                return int(enum_type(value))
            except ValueError as err:
                raise LgValueValidationError(
                    f"{value!r} is not a valid {enum_type.__name__}"
                ) from err

        validator = validate

    field = _enum(address, enum_type, writable=validator)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="enum",
            description=description,
            writable=writable,
            enum=EnumMetadata(
                enum_type=enum_type, options=options_from_enum(enum_type)
            ),
        ),
    )


def coil(
    address: int,
    *,
    writable: bool = False,
    description: str | None = None,
) -> CoilField:
    """Declare a coil (FC01/FC05)."""
    field = _coil(address, writable=writable)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="boolean",
            description=description,
            writable=writable,
            boolean=BooleanMetadata(),
        ),
    )


def discrete_input(
    address: int, *, description: str | None = None
) -> DiscreteInputField:
    """Declare a discrete input (FC02, read-only)."""
    field = _discrete_input(address)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="boolean",
            description=description,
            boolean=BooleanMetadata(),
        ),
    )


class LgComponent(Component):
    """A heat pump sub-system, with metadata lookup on top of ``Component``.

    Every field declared through the helpers in this module carries a
    :class:`~lg_heatpump_modbus.metadata.DatapointMetadata`. The component
    completes it with the register space and absolute address the framework
    resolved the field to.
    """

    def metadata_for(self, field: str) -> DatapointMetadata | None:
        """Return the metadata for one field, or ``None`` if it carries none."""
        declared = self.declared_fields.get(field)
        metadata: DatapointMetadata | None = getattr(declared, "lg_metadata", None)
        if metadata is None:
            return None
        if (resolved := self.resolved_fields.get(field)) is None:
            return metadata
        space = "discrete" if resolved.space == "discrete" else resolved.space
        return replace(metadata, register_type=space, address=resolved.address)

    def require_metadata_for(self, field: str) -> DatapointMetadata:
        """Return the metadata for one field, raising if it carries none."""
        if (metadata := self.metadata_for(field)) is None:
            raise KeyError(f"{type(self).__name__} has no metadata for {field!r}")
        return metadata

    @property
    def datapoints(self) -> Mapping[str, DatapointMetadata]:
        """Return the metadata of every declared datapoint, in declaration order."""
        return {
            name: metadata
            for name in self.declared_fields
            if (metadata := self.metadata_for(name)) is not None
        }

    @property
    def writable_datapoints(self) -> tuple[str, ...]:
        """Return the names of the datapoints that can be written."""
        return tuple(
            name for name, metadata in self.datapoints.items() if metadata.writable
        )

    def values(self) -> dict[str, Any]:
        """Return the decoded value of every declared field."""
        return {name: getattr(self, name) for name in self.declared_fields}

    def available_datapoints(self) -> tuple[str, ...]:
        """Return the fields that currently hold a value."""
        return tuple(
            name for name in self.declared_fields if getattr(self, name) is not None
        )

    def restrict_to(self, names: Iterable[str]) -> None:
        """Narrow this component to ``names``, ignoring fields it never declared."""
        declared = self.declared_fields
        self.restrict_fields([name for name in names if name in declared])
