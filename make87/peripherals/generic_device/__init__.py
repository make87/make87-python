"""Generic device peripheral implementation for Make87 hardware control.

This module provides the GenericDevicePeripheral class for managing generic
hardware devices in Make87 applications through direct device node access.
"""

from make87.models import GenericDevicePeripheral as GenericDevicePeripheralModel
from make87.peripherals.base import PeripheralBase


class GenericDevicePeripheral(PeripheralBase):
    """Generic device peripheral for Make87 hardware control.

    This class represents a generic hardware device in the Make87 system,
    providing basic device node access for devices that don't fit into
    specific peripheral categories.

    Attributes:
        name: The name identifier for this generic device peripheral
        device_node: The device node path for hardware access
    """

    def __init__(self, name: str, device_node: str):
        """Initialize the generic device peripheral with device node configuration.

        Args:
            name: The name identifier for this generic device peripheral
            device_node: The device node path (e.g., "/dev/ttyUSB0", "/dev/spidev0.0")

        Example:

            >>> device = GenericDevicePeripheral(
            ...     name="serial_port",
            ...     device_node="/dev/ttyUSB0"
            ... )
        """
        super().__init__(name)
        self.device_node = device_node

    @classmethod
    def from_config(cls, config: GenericDevicePeripheralModel):
        """Create a GenericDevicePeripheral instance from configuration model.

        Factory method that creates a GenericDevicePeripheral instance from a
        GenericDevicePeripheralModel configuration object.

        Args:
            config: GenericDevicePeripheralModel configuration object

        Returns:
            GenericDevicePeripheral instance configured according to the model

        Example:

            >>> from make87.models import GenericDevicePeripheralModel
            >>> config = GenericDevicePeripheralModel(...)
            >>> device = GenericDevicePeripheral.from_config(config)
        """
        generic = config.GenericDevice
        return cls(
            name=generic.name,
            device_node=generic.device_node,
        )
