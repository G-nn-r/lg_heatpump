"""Common fixtures for the LG Heat Pump tests.

Every test runs against ``modbus-connection``'s in-memory mock backend, so the
whole suite needs no hardware, no server and no network. Only the connection that
Home Assistant's shared ``modbus`` helpers build is replaced — the device library, the
coordinators and the entity platforms are the real thing.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

from modbus_connection.mock import MockModbusConnection
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lg_heatpump.const import DOMAIN

from . import MOCK_UNIT_ID, MOCK_USER_INPUT, seed_heat_pump

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

CREATE_CONNECTION = "homeassistant.components.modbus.connection.ModbusConnection"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> None:
    """Load custom_components/lg_heatpump in every test."""
    return


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.lg_heatpump.async_setup_entry",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_connection() -> MockModbusConnection:
    """Return an in-memory Modbus connection seeded as an LG heat pump."""
    connection = MockModbusConnection()
    seed_heat_pump(connection.for_unit(MOCK_UNIT_ID))
    # The shared connection closes when its last holder unloads. A closed mock
    # connection refuses every later request, and tests reload the entry against
    # the same seeded stores, so closing is recorded rather than performed.
    # test_init asserts that the close actually happens.
    connection.close = AsyncMock()  # type: ignore[method-assign]
    return connection


@pytest.fixture
def mock_unit(mock_connection: MockModbusConnection):
    """Return the seeded unit, to assert on the stores a write landed in."""
    return mock_connection.for_unit(MOCK_UNIT_ID)


@pytest.fixture
def patched_connection(
    mock_connection: MockModbusConnection,
) -> Generator[None]:
    """Build the in-memory connection instead of a real Modbus TCP one."""
    with patch(CREATE_CONNECTION, return_value=mock_connection):
        yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mocked LG Heat Pump config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="LG Therma V",
        data=MOCK_USER_INPUT,
    )


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    patched_connection: None,
) -> MockConfigEntry:
    """Set up the LG Heat Pump integration for testing."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done(wait_background_tasks=True)
    return mock_config_entry
