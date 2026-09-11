"""lg-heatpump-modbus — read and control LG heat pumps over Modbus.

Construct :class:`LgHeatPump` with a ``modbus_connection.ModbusUnit``, call
``await pump.async_update()``, then read its sub-systems as plain Python
attributes::

    pump.sensors.outdoor_temperature
    pump.states.compressor
    pump.controls.target_temperature_circuit_1

Writing goes the same way::

    await pump.controls.set_dhw_target_temperature(48.0)
    await pump.switches.set_silent_mode(True)

The library never owns the transport. Build a connection with whichever
``modbus-connection`` backend suits the application, hand a unit to
:class:`LgHeatPump`, and close the connection yourself.
"""

from .configurations import (
    DEFAULT_MODEL,
    MODELS,
    THERMA_V,
    THERMA_V_HEATING_ONLY,
    THERMA_V_SINGLE_CIRCUIT,
    ModelDefinition,
    get_model,
)
from .data_model import LgComponent
from .enums import Circuit, ControlMethod, EnergyState, OperationMode
from .exceptions import (
    LgFieldNotAvailableError,
    LgHeatPumpError,
    LgValueValidationError,
)
from .heatpump import (
    READING_COMPONENTS,
    SETTING_COMPONENTS,
    LgHeatPump,
    UpdateReport,
)
from .metadata import (
    BooleanMetadata,
    DatapointMetadata,
    EnumMetadata,
    NumberMetadata,
    OptionMetadata,
)
from .subsystems import Controls, DeviceInformation, Sensors, States, Switches

__all__ = [
    "DEFAULT_MODEL",
    "MODELS",
    "READING_COMPONENTS",
    "SETTING_COMPONENTS",
    "THERMA_V",
    "THERMA_V_HEATING_ONLY",
    "THERMA_V_SINGLE_CIRCUIT",
    "BooleanMetadata",
    "Circuit",
    "ControlMethod",
    "Controls",
    "DatapointMetadata",
    "DeviceInformation",
    "EnergyState",
    "EnumMetadata",
    "LgComponent",
    "LgFieldNotAvailableError",
    "LgHeatPump",
    "LgHeatPumpError",
    "LgValueValidationError",
    "ModelDefinition",
    "NumberMetadata",
    "OperationMode",
    "OptionMetadata",
    "Sensors",
    "States",
    "Switches",
    "UpdateReport",
    "get_model",
]
