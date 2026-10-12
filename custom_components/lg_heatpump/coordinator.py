"""DataUpdateCoordinators that poll the LG heat pump.

The measurements and the settings live in different Modbus tables and change at
very different rates, so each gets its own coordinator and its own interval.
Both drive the same ``LgHeatPump`` object, which is what the entities read.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, override

from modbus_connection import ModbusError

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import utcnow

from .const import DOMAIN, LOGGER, MANUFACTURER
from .lg_heatpump_modbus import SETTING_COMPONENTS, UpdateReport

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from datetime import timedelta

    from modbus_connection.tmodbus import ModbusConnection

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .lg_heatpump_modbus import LgHeatPump

type LgHeatPumpConfigEntry = ConfigEntry[LgHeatPumpRuntimeData]


class LgHeatPumpCoordinator(DataUpdateCoordinator[UpdateReport]):
    """Refresh a set of the heat pump's sub-systems on a schedule.

    Each sub-system reads only its own registers, so one that stops answering
    keeps its previous values and does not take the rest of the poll with it.
    """

    config_entry: LgHeatPumpConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: LgHeatPumpConfigEntry,
        device: LgHeatPump,
        poll: Callable[[], Awaitable[UpdateReport]],
        interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=entry.title,
            update_interval=interval,
        )
        self.device = device
        self._poll = poll
        self._consecutive_failures: dict[str, int] = {}
        self.last_poll_time: datetime | None = None
        """When the last poll finished, whether it succeeded or not."""

    @callback
    @override
    def _async_refresh_finished(self) -> None:
        """Remember when a poll ended, for the debug timestamp sensor."""
        self.last_poll_time = utcnow()

    @property
    def device_info(self) -> dr.DeviceInfo:
        """Return the device the heat pump's entities belong to."""
        entry = self.config_entry
        return dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=self.device.model_name,
            # The unit may refuse the identity registers; fall back to the chosen model.
            model_id=self.device.info.product_code or self.device.model.key,
            name=entry.title,
        )

    async def _async_update_data(self) -> UpdateReport:
        """Poll the heat pump, or fail the update if nothing answered."""
        try:
            report = await self._poll()
        except ModbusError as error:
            # A dead link or a device that answers nothing reaches here; a
            # single refused block lands in report.failed instead.
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="modbus_error",
                translation_placeholders={"error": str(error)},
            ) from error
        if not report.updated:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="no_component_answered",
            ) from ExceptionGroup(
                "no sub-system answered", list(report.failed.values())
            )
        self._log_transitions(report)
        return report

    def _log_transitions(self, report: UpdateReport) -> None:
        """Log a sub-system going quiet once, and log it coming back."""
        for name, cause in report.failed.items():
            previous = self._consecutive_failures.get(name, 0)
            self._consecutive_failures[name] = previous + 1
            if previous == 0:
                LOGGER.warning(
                    "%s: %s failed to refresh and is keeping its previous values: %s",
                    self.name,
                    name,
                    cause,
                )
        for name in report.updated:
            if self._consecutive_failures.pop(name, None) is not None:
                LOGGER.info("%s: %s is available again", self.name, name)


@dataclass
class LgHeatPumpRuntimeData:
    """Runtime data for a configured heat pump."""

    device: LgHeatPump
    connection: ModbusConnection
    readings: LgHeatPumpCoordinator
    settings: LgHeatPumpCoordinator

    def coordinator_for(self, component: str) -> LgHeatPumpCoordinator:
        """Return the coordinator that owns a sub-system's data."""
        return self.settings if component in SETTING_COMPONENTS else self.readings
