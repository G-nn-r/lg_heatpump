"""Device identity, read once at setup and never polled."""

from __future__ import annotations

from ..data_model import LgComponent, raw_register

MANUFACTURER = "LG"

# TODO is any information from here helpful? https://github.com/basti242/homeassistant_lg_therma_v_modbus/wiki/LG-Register-documentation

PRODUCT_GROUP_ADDRESS = 9997
PRODUCT_INFO_ADDRESS = 9998


class DeviceInformation(LgComponent):
    """The identity words the outdoor unit reports."""

    register_space = "input"
    register_ranges = ((PRODUCT_GROUP_ADDRESS, PRODUCT_INFO_ADDRESS),)

    # TODO verify
    product_group = raw_register(
        PRODUCT_GROUP_ADDRESS,
        description="Product group code reported by the outdoor unit",
    )
    """Product group code, e.g. 0x80, 0x83, 0x88 or 0x89."""

    # TODO verify
    product_info = raw_register(
        PRODUCT_INFO_ADDRESS,
        description="Device information word: split, monoblock, high-temp, mid-temp, system-boiler",
    )
    """
    Device information word, as reported by the outdoor unit.
    Supposed to be:
    0: Split
    3: Monobloc
    4: High Temp.
    5: Medium Temp.
    6: System Boiler
    """

    @property
    def manufacturer(self) -> str:
        """Return the manufacturer name."""
        return MANUFACTURER

    @property
    def device_info(self) -> int | None:
        """Return the device information word as an alias for :attr:`product_info`."""
        return self.product_info

    @property
    def product_code(self) -> str | None:
        """Return the product group code as a hexadecimal string."""
        if (value := self.product_group) is None:
            return None
        return f"0x{value:04X}"
