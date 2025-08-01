"""I2C peripheral implementation for Make87 hardware control.

This module provides the I2cPeripheral class for managing I2C bus devices
in Make87 applications, including bus configuration, device detection,
and device node access.
"""

from typing import List

from make87.models import I2cPeripheral as I2cPeripheralModel
from make87.peripherals.base import PeripheralBase


class I2cPeripheral(PeripheralBase):
    """I2C peripheral device for Make87 hardware control.

    This class represents an I2C (Inter-Integrated Circuit) bus device in the
    Make87 system, providing access to I2C communication through device nodes
    and managing detected devices on the bus.

    Attributes:
        name: The name identifier for this I2C peripheral
        bus_number: The I2C bus number
        device_nodes: List of device node paths for I2C access
        detected_devices: List of detected I2C device configurations
    """

    def __init__(
        self,
        name: str,
        bus_number: int,
        device_nodes: List[str],
        detected_devices: List[dict],
    ):
        """Initialize the I2C peripheral with bus and device configuration.

        Args:
            name: The name identifier for this I2C peripheral
            bus_number: The I2C bus number (e.g., 0 for /dev/i2c-0)
            device_nodes: List of device node paths (e.g., ["/dev/i2c-0"])
            detected_devices: List of detected I2C device configuration dictionaries,
                each containing device address and other properties

        Example:

            >>> i2c = I2cPeripheral(
            ...     name="main_i2c",
            ...     bus_number=1,
            ...     device_nodes=["/dev/i2c-1"],
            ...     detected_devices=[
            ...         {"address": "0x48", "name": "TMP102"},
            ...         {"address": "0x68", "name": "DS3231"}
            ...     ]
            ... )
        """
        super().__init__(name)
        self.bus_number = bus_number
        self.device_nodes = device_nodes
        self.detected_devices = detected_devices

    @classmethod
    def from_config(cls, config: I2cPeripheralModel):
        """Create an I2cPeripheral instance from configuration model.

        Factory method that creates an I2cPeripheral instance from an
        I2cPeripheralModel configuration object.

        Args:
            config: I2cPeripheralModel configuration object

        Returns:
            I2cPeripheral instance configured according to the model

        Example:

            >>> from make87.models import I2cPeripheralModel
            >>> config = I2cPeripheralModel(...)
            >>> i2c = I2cPeripheral.from_config(config)
        """
        i2c = config.I2C
        return cls(
            name=i2c.name,
            bus_number=i2c.bus_number,
            device_nodes=i2c.device_nodes,
            detected_devices=[d.model_dump() for d in i2c.detected_devices],
        )
