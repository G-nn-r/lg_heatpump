"""Tests for the LG Heat Pump config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from modbus_connection import ModbusTimeoutError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lg_heatpump.const import (
    CONF_DEBUG,
    CONF_MODEL,
    CONF_UNIT_ID,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType

from . import MOCK_HOST, MOCK_PORT, MOCK_UNIT_ID, MOCK_USER_INPUT

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from modbus_connection.mock import MockModbusConnection, MockModbusUnit

    from homeassistant.core import HomeAssistant

FLOW_CONNECTION = "homeassistant.components.modbus.connection.ModbusConnection"


async def test_user_flow(
    hass: HomeAssistant,
    mock_connection: MockModbusConnection,
    mock_setup_entry: AsyncMock,
) -> None:
    """A reachable heat pump creates an entry titled with its model."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(FLOW_CONNECTION, return_value=mock_connection):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], MOCK_USER_INPUT
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "LG Therma V"
    assert result["data"] == {**MOCK_USER_INPUT, CONF_DEBUG: False}
    assert len(mock_setup_entry.mock_calls) == 1


async def test_user_flow_cannot_connect(
    hass: HomeAssistant,
    mock_connection: MockModbusConnection,
    mock_unit: MockModbusUnit,
    mock_setup_entry: AsyncMock,
) -> None:
    """A heat pump that does not answer surfaces cannot_connect, then recovers."""
    mock_unit.fail_requests(ModbusTimeoutError())

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    with patch(FLOW_CONNECTION, return_value=mock_connection):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], MOCK_USER_INPUT
        )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}

        mock_unit.fail_requests(None)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], MOCK_USER_INPUT
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_already_configured(
    hass: HomeAssistant,
    mock_connection: MockModbusConnection,
    mock_config_entry: MockConfigEntry,
) -> None:
    """The same host, port and unit cannot be added twice."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    with patch(FLOW_CONNECTION, return_value=mock_connection):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], MOCK_USER_INPUT
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_flow(
    hass: HomeAssistant,
    mock_connection: MockModbusConnection,
    init_integration: MockConfigEntry,
) -> None:
    """Reconfiguring updates the connection details in place."""
    result = await init_integration.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    with patch(FLOW_CONNECTION, return_value=mock_connection):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.60",
                CONF_PORT: MOCK_PORT,
                CONF_UNIT_ID: MOCK_UNIT_ID,
                CONF_MODEL: "therma_v_single_circuit",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert init_integration.data[CONF_HOST] == "192.168.1.60"
    assert init_integration.data[CONF_MODEL] == "therma_v_single_circuit"


async def test_reconfigure_flow_cannot_connect(
    hass: HomeAssistant,
    mock_connection: MockModbusConnection,
    mock_unit: MockModbusUnit,
    init_integration: MockConfigEntry,
) -> None:
    """Reconfiguring onto an unreachable heat pump keeps the old settings."""
    mock_unit.fail_requests(ModbusTimeoutError())

    result = await init_integration.start_reconfigure_flow(hass)
    with patch(FLOW_CONNECTION, return_value=mock_connection):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.60",
                CONF_PORT: MOCK_PORT,
                CONF_UNIT_ID: MOCK_UNIT_ID,
                CONF_MODEL: "therma_v",
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert init_integration.data[CONF_HOST] == MOCK_HOST
