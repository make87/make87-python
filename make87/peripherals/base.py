"""Base peripheral classes for make87 hardware control.

This module provides the abstract base class for all make87 peripheral
devices, defining the common interface for hardware peripherals.
"""

from abc import ABC


class PeripheralBase(ABC):
    """Abstract base class for all make87 peripheral devices.

    This class provides a common foundation for all make87 peripheral
    devices, establishing a consistent interface for hardware control
    and management.

    Attributes:
        name: The name identifier for this peripheral instance
    """

    def __init__(self, name: str):
        """Initialize the peripheral with a name identifier.

        Args:
            name: The name identifier for this peripheral instance
        """
        self.name = name
