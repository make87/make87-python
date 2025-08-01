"""Other peripheral implementation for Make87 hardware control.

This module provides the OtherPeripheral class for managing miscellaneous
hardware devices in Make87 applications that don't fit into specific
peripheral categories.
"""

from typing import List

from make87.models import OtherPeripheral as OtherPeripheralModel
from make87.peripherals.base import PeripheralBase


class OtherPeripheral(PeripheralBase):
    """Other peripheral device for Make87 hardware control.

    This class represents miscellaneous hardware devices in the Make87 system
    that don't fit into specific peripheral categories. It provides basic
    device node access and reference management for various hardware types.

    Attributes:
        name: The name identifier for this peripheral
        reference: Reference identifier or description for the device
        device_nodes: List of device node paths for hardware access
    """

    def __init__(
        self,
        name: str,
        reference: str,
        device_nodes: List[str],
    ):
        """Initialize the other peripheral with device configuration.

        Args:
            name: The name identifier for this peripheral
            reference: Reference identifier or description for the device
                (e.g., "power_management", "watchdog_timer")
            device_nodes: List of device node paths for hardware access
                (e.g., ["/dev/watchdog0"])

        Example:

            >>> other = OtherPeripheral(
            ...     name="system_watchdog",
            ...     reference="hardware_watchdog_timer",
            ...     device_nodes=["/dev/watchdog0"]
            ... )
        """
        super().__init__(name)
        self.reference = reference
        self.device_nodes = device_nodes

    @classmethod
    def from_config(cls, config: OtherPeripheralModel):
        """Create an OtherPeripheral instance from configuration model.

        Factory method that creates an OtherPeripheral instance from an
        OtherPeripheralModel configuration object.

        Args:
            config: OtherPeripheralModel configuration object

        Returns:
            OtherPeripheral instance configured according to the model

        Example:

            >>> from make87.models import OtherPeripheralModel
            >>> config = OtherPeripheralModel(...)
            >>> other = OtherPeripheral.from_config(config)
        """
        other = config.Other
        return cls(
            name=other.name,
            reference=other.reference,
            device_nodes=other.device_nodes,
        )
