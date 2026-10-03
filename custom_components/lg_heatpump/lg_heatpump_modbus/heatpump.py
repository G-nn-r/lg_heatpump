"""The top-level :class:`LgHeatPump` device object."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from modbus_connection import (
    IllegalDataAddressError,
    IllegalFunctionError,
    ModbusConnectionError,
    ModbusError,
    ModbusTimeoutError,
)

from .configurations.models import DEFAULT_MODEL, ModelDefinition, get_model
from .data_model import LgComponent
from .subsystems import Controls, DeviceInformation, Sensors, States, Switches

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

#: Sub-systems refreshed by :meth:`LgHeatPump.async_update_readings`.
READING_COMPONENTS: tuple[str, ...] = ("sensors", "states")

#: Sub-systems refreshed by :meth:`LgHeatPump.async_update_settings`.
SETTING_COMPONENTS: tuple[str, ...] = ("controls", "switches")


@dataclass
class UpdateReport:
    """What one poll managed to refresh."""

    updated: list[str] = field(default_factory=list)
    failed: dict[str, ModbusError] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """Return whether every sub-system polled answered."""
        return not self.failed


class LgHeatPump:
    """An LG heat pump reached through a ``ModbusUnit``.

    The library never opens or closes a connection. A consumer builds a
    ``ModbusUnit`` with whichever ``modbus-connection`` backend it prefers and
    passes it in; the heat pump only reads and writes registers on it.

        >>> pump = LgHeatPump(unit)                       # doctest: +SKIP
        >>> await pump.async_update()                     # doctest: +SKIP
        >>> pump.sensors.outdoor_temperature              # doctest: +SKIP
        4.2
        >>> await pump.controls.set_dhw_target_temperature(48)   # doctest: +SKIP
    """

    def __init__(
        self,
        unit: ModbusUnit,
        *,
        model: ModelDefinition | str = DEFAULT_MODEL,
        excluded_datapoints: Iterable[str] = (),
        debug: bool = False,
    ) -> None:
        """Build a heat pump on ``unit``, serving what ``model`` describes.

        ``debug`` disables sentinel masking (see
        :func:`~lg_heatpump_modbus.data_model.hide_sentinel`) across every
        sub-system, so a datapoint that normally reads as ``None`` instead
        returns the raw value the heat pump reported. Toggle it later through
        the :attr:`debug` property.
        """
        self._unit = unit
        self.model = get_model(model) if isinstance(model, str) else model
        self.excluded_datapoints = frozenset(excluded_datapoints)

        self.info = DeviceInformation(unit)
        self.sensors = Sensors(unit)
        self.states = States(unit)
        self.controls = Controls(unit)
        self.switches = Switches(unit)

        self._is_set_up = False
        for component in self.components:
            self._restrict(component)
        self.debug = debug

    @property
    def debug(self) -> bool:
        """Whether sentinel masking is disabled across every sub-system."""
        return self.sensors.debug

    @debug.setter
    def debug(self, value: bool) -> None:
        for component in self.components:
            component.debug = value

    @property
    def components(self) -> tuple[LgComponent, ...]:
        """Return every sub-system, identity first."""
        return (self.info, self.sensors, self.states, self.controls, self.switches)

    @property
    def component_names(self) -> tuple[str, ...]:
        """Return the attribute name of every sub-system, identity first."""
        return ("info", *READING_COMPONENTS, *SETTING_COMPONENTS)

    @property
    def water_outlet_temperature_circuit_1(self) -> float | None:
        """
        Return the water outlet temperature of circuit 1.

        Circuit 1 is the primary, unmixed circuit, so this value is normally just an alias to
        ``sensors.water_outlet_temperature``. While the heat pump is heating domestic hot water,
        that shared sensor reflects the DHW loop instead, so this returns ``None`` in that case.
        """
        return None if self.states.dhw_heating else self.sensors.water_outlet_temperature

    @property
    def manufacturer(self) -> str:
        """Return the manufacturer name."""
        return self.info.manufacturer

    @property
    def model_name(self) -> str:
        """Return the human-readable model name."""
        return self.model.name

    def serves(self, datapoint: str) -> bool:
        """Return whether this heat pump serves ``datapoint``."""
        return (
            self.model.serves(datapoint) and datapoint not in self.excluded_datapoints
        )

    def _restrict(self, component: LgComponent) -> None:
        """Narrow a component to the datapoints this heat pump serves."""
        served = [name for name in component.declared_fields if self.serves(name)]
        if len(served) != len(component.declared_fields):
            component.restrict_fields(served)

    async def _async_setup(self) -> None:
        """Read what never changes.

        Identity is optional: a unit that refuses input register 9998 is still
        a working heat pump, so a refusal is remembered rather than raised.
        """
        try:
            await self.info.async_update()
        except (IllegalDataAddressError, IllegalFunctionError):
            pass
        self._is_set_up = True

    async def _async_poll(
        self, names: tuple[str, ...], report: UpdateReport
    ) -> UpdateReport:
        """Read each named sub-system on its own, recording what happened."""
        for name in names:
            try:
                await getattr(self, name).async_update(notify=False)
            except ModbusConnectionError:
                raise  # the link is down; the rest would only wait for timeouts
            except ModbusTimeoutError as err:
                if not report.updated and not report.failed:
                    raise  # nothing answered yet: assume the rest time out too
                report.failed[name] = err
            except ModbusError as err:
                report.failed[name] = err
            else:
                report.updated.append(name)
        return report

    def _notify(self, report: UpdateReport) -> None:
        """Fire the listeners of everything this update refreshed."""
        for name in report.updated:
            getattr(self, name).notify()

    async def async_update_readings(self) -> UpdateReport:
        """Refresh what the heat pump measures and reports."""
        if not self._is_set_up:
            await self._async_setup()
        report = await self._async_poll(READING_COMPONENTS, UpdateReport())
        self._notify(report)
        return report

    async def async_update_settings(self) -> UpdateReport:
        """Refresh what the heat pump has been configured to do."""
        if not self._is_set_up:
            await self._async_setup()
        report = await self._async_poll(SETTING_COMPONENTS, UpdateReport())
        self._notify(report)
        return report

    async def async_update(self) -> UpdateReport:
        """Refresh every polled sub-system."""
        if not self._is_set_up:
            await self._async_setup()
        report = await self._async_poll(READING_COMPONENTS, UpdateReport())
        await self._async_poll(SETTING_COMPONENTS, report)
        self._notify(report)
        return report

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Return every register this heat pump reads, undecoded, for diagnostics."""
        if not self._is_set_up:
            await self._async_setup()
        raw: dict[str, dict[int, int | bool]] = {}
        for name in self.component_names:
            read = await getattr(self, name).async_read_raw(notify=False)
            for space, values in read.items():
                raw.setdefault(space, {}).update(values)
        return raw

    # TODO add "sync now" button in HA
