from abc import ABC

from make87.models.application_env_config import ApplicationEnvConfig
from make87.peripherals.factory import create_peripheral_from_data


class PeripheralBase(ABC):
    def __init__(self, name: str):
        self.name = name


class PeripheralManager:
    def __init__(self, config: ApplicationEnvConfig):
        self._config = config
        self._peripherals = self._build_registry()

    def _build_registry(self):
        registry = {}
        for mp in self._config.peripherals.peripherals:
            # Use a factory to create specific Peripheral subclass
            registry[mp.name] = create_peripheral_from_data(mp)
        return registry

    def get_peripheral_by_name(self, name: str) -> PeripheralBase:
        return self._peripherals[name]

    def list_peripherals(self):
        return list(self._peripherals.values())

    def __iter__(self):
        # Allows: list(PeripheralManager) -> list of PeripheralBase
        return iter(self._peripherals.values())

    def __getitem__(self, key):
        # Allows: dict(PeripheralManager)['name'] -> PeripheralBase
        return self._peripherals[key]

    def __len__(self):
        return len(self._peripherals)

    def __contains__(self, key):
        return key in self._peripherals

    def items(self):
        # Allows: dict(PeripheralManager).items()
        return self._peripherals.items()
