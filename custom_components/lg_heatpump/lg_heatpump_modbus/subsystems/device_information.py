"""Device identity, read once at setup and never polled."""

from __future__ import annotations

from ..data_model import LgComponent, raw_register

MANUFACTURER = "LG"

#: Input register holding the packed product information word.
PRODUCT_INFO_ADDRESS = 9998


class DeviceInformation(LgComponent):
    """The product information word the outdoor unit reports."""

    register_space = "input"
    register_ranges = ((PRODUCT_INFO_ADDRESS, PRODUCT_INFO_ADDRESS),)

    product_info = raw_register(
        PRODUCT_INFO_ADDRESS, description="Packed product information word"
    )
    """Packed product information word, as reported by the outdoor unit."""

    @property
    def manufacturer(self) -> str:
        """Return the manufacturer name."""
        return MANUFACTURER

    @property
    def product_code(self) -> str | None:
        """Return the product information word as a hexadecimal string."""
        if (value := self.product_info) is None:
            return None
        return f"0x{value:04X}"
