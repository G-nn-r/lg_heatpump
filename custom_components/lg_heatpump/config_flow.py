"""Config flow for the LG Heat Pump custom integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from modbus_connection import ModbusError
import voluptuous as vol

from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .connection import create_modbus_params
from .const import (
    CONF_DEBUG,
    CONF_MODEL,
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DOMAIN,
)
from .lg_heatpump_modbus import MODELS, LgHeatPump

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): TextSelector(),
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            NumberSelector(
                NumberSelectorConfig(mode=NumberSelectorMode.BOX, min=1, max=65535)
            ),
            vol.Coerce(int),
        ),
        vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): vol.All(
            NumberSelector(
                NumberSelectorConfig(mode=NumberSelectorMode.BOX, min=1, max=247)
            ),
            vol.Coerce(int),
        ),
        vol.Required(CONF_MODEL, default="therma_v"): SelectSelector(
            SelectSelectorConfig(
                options=[
                    SelectOptionDict(value=key, label=model.name)
                    for key, model in MODELS.items()
                ],
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_DEBUG, default=False): BooleanSelector(),
    }
)


async def _async_probe(hass: HomeAssistant, data: dict[str, Any]) -> LgHeatPump:
    """Read the heat pump once to prove it is reachable, or raise.

    The unit is held only while probing: the config flow has no config entry
    yet to tie it to.
    """
    async with async_get_temporary_unit(
        hass,
        create_modbus_params(data),
        data[CONF_UNIT_ID],
    ) as unit:
        device = LgHeatPump(
            unit,
            model=data[CONF_MODEL],
            debug=data.get(CONF_DEBUG, False),
        )
        await device.sensors.async_update()
    return device


class LgHeatPumpConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for an LG heat pump."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Collect the connection details and check the heat pump answers."""
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}
        if user_input is not None:
            self._async_abort_entries_match(
                {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_UNIT_ID: user_input[CONF_UNIT_ID],
                }
            )
            try:
                device = await _async_probe(self.hass, user_input)
            except ModbusError as error:
                errors["base"] = "cannot_connect"
                placeholders["error"] = str(error)
            except OSError as error:  # pragma: no cover - transport-specific
                errors["base"] = "cannot_connect"
                placeholders["error"] = str(error)
            else:
                return self.async_create_entry(title=device.model_name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA, user_input
            ),
            errors=errors,
            description_placeholders=placeholders,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Update an existing entry's connection details or model."""
        reconfigure_entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}
        if user_input is not None:
            try:
                await _async_probe(self.hass, user_input)
            except (ModbusError, OSError) as error:
                errors["base"] = "cannot_connect"
                placeholders["error"] = str(error)
            else:
                return self.async_update_reload_and_abort(
                    reconfigure_entry, data_updates=user_input
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA, user_input or reconfigure_entry.data
            ),
            errors=errors,
            description_placeholders=placeholders,
        )
