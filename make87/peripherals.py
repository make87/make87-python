import json
import os
import threading
from typing import List, Union, Dict

from pydantic import BaseModel


class Peripheral(BaseModel):
    name: str
    mount: Union[str, int]


class Peripherals(BaseModel):
    peripherals: List[Peripheral]


class _PeripheralManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._peripheral_mounts: Dict[str, str] = {}
        self._initialized: bool = False

    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure only one instance exists."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def initialize(self):
        """Initialize the peripherals."""
        with self._lock:
            if self._initialized:
                return  # Already initialized

            try:
                peripheral_data_env = os.environ.get("PERIPHERALS", '{"peripherals":[]}')
                peripheral_data = Peripherals.model_validate_json(peripheral_data_env)
            except json.JSONDecodeError:
                raise ValueError("`PERIPHERALS` environment variable is not valid JSON.")

            for peripheral in peripheral_data.peripherals:
                self._peripheral_mounts[peripheral.name] = peripheral.mount

            self._initialized = True

    def resolve_peripheral_name(self, name: str) -> str:
        """Resolve a peripheral name to its mount."""
        if not self._initialized:
            raise ValueError("PeripheralManager not initialized.")
        if name not in self._peripheral_mounts:
            raise ValueError(f"Peripheral {name} not found.")
        return self._peripheral_mounts.get(name, name)


def resolve_peripheral_name(name: str) -> str:
    """Resolve a peripheral name to its mount location.

    Args:
        name: Name of peripheral used in the `MAKE87.yml` file.

    Returns:
        The mount path or name of the peripheral on the node.
    """
    return _PeripheralManager.get_instance().resolve_peripheral_name(name)
