"""Peripheral management for Make87 hardware devices.

This module provides the PeripheralManager class for managing and accessing
hardware peripheral devices in Make87 applications. It handles peripheral
discovery, creation, and provides a convenient interface for accessing
configured peripherals.
"""

from typing import Optional

from make87.config import load_config_from_env
from make87.models import ApplicationConfig
from make87.peripherals import PeripheralBase
from make87.peripherals.factory import create_peripheral_from_data


class PeripheralManager:
    """Manager for Make87 hardware peripheral devices.

    This class provides centralized management of hardware peripheral devices,
    automatically discovering and creating peripheral instances based on the
    application configuration. It offers dictionary-like access to peripherals
    and supports iteration over all managed devices.

    Attributes:
        _config: The Make87 application configuration
        _peripherals: Registry of created peripheral instances
    """

    def __init__(self, make87_config: Optional[ApplicationConfig] = None):
        """Initialize the peripheral manager with application configuration.

        Args:
            make87_config: Optional ApplicationConfig instance. If not provided,
                configuration will be loaded from the environment.
        """
        if make87_config is None:
            make87_config = load_config_from_env()
        self._config = make87_config
        self._peripherals = self._build_registry()

    def _build_registry(self):
        """Build the internal registry of peripheral instances.

        Creates peripheral instances for all peripherals defined in the
        application configuration using the peripheral factory.

        Returns:
            Dictionary mapping peripheral names to peripheral instances
        """
        registry = {}
        for mp in self._config.peripherals.peripherals:
            # Use a factory to create specific Peripheral subclass
            registry[mp.name] = create_peripheral_from_data(mp)
        return registry

    def get_peripheral_by_name(self, name: str) -> PeripheralBase:
        """Get a peripheral instance by name.

        Args:
            name: The name of the peripheral to retrieve

        Returns:
            The peripheral instance with the specified name

        Raises:
            KeyError: If no peripheral with the given name exists

        Example:

            >>> manager = PeripheralManager()
            >>> camera = manager.get_peripheral_by_name("main_camera")
            >>> gpio = manager.get_peripheral_by_name("status_led")
        """
        return self._peripherals[name]

    def list_peripherals(self):
        """Get a list of all managed peripheral instances.

        Returns:
            List of all PeripheralBase instances managed by this manager

        Example:

            >>> manager = PeripheralManager()
            >>> peripherals = manager.list_peripherals()
            >>> for peripheral in peripherals:
            ...     print(f"Peripheral: {peripheral.name}")
        """
        return list(self._peripherals.values())

    def __iter__(self):
        """Iterator over all peripheral instances.

        Enables iteration over the manager to access all peripheral instances.

        Returns:
            Iterator over PeripheralBase instances

        Example:

            >>> manager = PeripheralManager()
            >>> for peripheral in manager:
            ...     print(f"Found peripheral: {peripheral.name}")
        """
        return iter(self._peripherals.values())

    def __getitem__(self, key):
        """Dictionary-style access to peripherals by name.

        Args:
            key: The name of the peripheral to retrieve

        Returns:
            The peripheral instance with the specified name

        Raises:
            KeyError: If no peripheral with the given name exists

        Example:

            >>> manager = PeripheralManager()
            >>> camera = manager["main_camera"]
            >>> led = manager["status_led"]
        """
        return self._peripherals[key]

    def __len__(self):
        """Get the number of managed peripherals.

        Returns:
            The number of peripheral instances managed by this manager

        Example:

            >>> manager = PeripheralManager()
            >>> print(f"Managing {len(manager)} peripherals")
        """
        return len(self._peripherals)

    def __contains__(self, key):
        """Check if a peripheral with the given name exists.

        Args:
            key: The name of the peripheral to check for

        Returns:
            True if a peripheral with the given name exists, False otherwise

        Example:

            >>> manager = PeripheralManager()
            >>> if "main_camera" in manager:
            ...     print("Camera is available")
        """
        return key in self._peripherals

    def items(self):
        """Get name-peripheral pairs for all managed peripherals.

        Returns:
            Dictionary items view of name-peripheral pairs

        Example:

            >>> manager = PeripheralManager()
            >>> for name, peripheral in manager.items():
            ...     print(f"{name}: {type(peripheral).__name__}")
        """
        return self._peripherals.items()
