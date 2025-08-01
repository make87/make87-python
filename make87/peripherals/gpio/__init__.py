"""GPIO peripheral implementation for Make87 hardware control.

This module provides the GpioPeripheral class for managing GPIO (General Purpose
Input/Output) devices in Make87 applications, including GPIO chip configuration,
line management, and device node access.
"""

from typing import List, Optional

from make87.models import GpioPeripheral as GpioPeripheralModel
from make87.peripherals.base import PeripheralBase


class GpioPeripheral(PeripheralBase):
    """GPIO peripheral device for Make87 hardware control.

    This class represents a GPIO chip device in the Make87 system, providing
    access to GPIO functionality including individual GPIO lines, chip
    configuration, and device node management.

    Attributes:
        name: The name identifier for this GPIO peripheral
        chip_name: Name of the GPIO chip
        label: Human-readable label for the GPIO chip
        num_lines: Total number of GPIO lines available on this chip
        device_nodes: List of device node paths for GPIO access
        lines: List of individual GPIO line configurations
    """

    def __init__(
        self,
        chip_name: str,
        label: str,
        num_lines: int,
        device_nodes: List[str],
        lines: List[dict],
        name: Optional[str] = None,
    ):
        """Initialize the GPIO peripheral with chip and line configuration.

        Args:
            chip_name: Name of the GPIO chip (e.g., "gpiochip0")
            label: Human-readable label for the GPIO chip
            num_lines: Total number of GPIO lines available on this chip
            device_nodes: List of device node paths (e.g., ["/dev/gpiochip0"])
            lines: List of individual GPIO line configuration dictionaries
            name: Optional custom name for the peripheral. If not provided,
                the label will be used as the name.

        Example:

            >>> gpio = GpioPeripheral(
            ...     chip_name="gpiochip0",
            ...     label="Main GPIO Chip",
            ...     num_lines=32,
            ...     device_nodes=["/dev/gpiochip0"],
            ...     lines=[
            ...         {"offset": 18, "name": "LED", "direction": "output"},
            ...         {"offset": 19, "name": "BUTTON", "direction": "input"}
            ...     ],
            ...     name="main_gpio"
            ... )
        """
        super().__init__(name or label)
        self.chip_name = chip_name
        self.label = label
        self.num_lines = num_lines
        self.device_nodes = device_nodes
        self.lines = lines

    @classmethod
    def from_config(cls, config: GpioPeripheralModel):
        """Create a GpioPeripheral instance from configuration model.

        Factory method that creates a GpioPeripheral instance from a
        GpioPeripheralModel configuration object.

        Args:
            config: GpioPeripheralModel configuration object

        Returns:
            GpioPeripheral instance configured according to the model

        Example:

            >>> from make87.models import GpioPeripheralModel
            >>> config = GpioPeripheralModel(...)
            >>> gpio = GpioPeripheral.from_config(config)
        """
        gpio = config.GPIO
        return cls(
            chip_name=gpio.chip_name,
            label=gpio.label,
            num_lines=gpio.num_lines,
            device_nodes=gpio.device_nodes,
            lines=[line.model_dump() for line in gpio.lines],
            name=gpio.name,
        )
