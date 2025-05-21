from typing import List

from make87.models.application_env_config import PeripheralOther
from make87.peripherals.base import PeripheralBase


class OtherPeripheral(PeripheralBase):
    def __init__(
        self,
        name: str,
        reference: str,
        device_nodes: List[str],
    ):
        super().__init__(name)
        self.reference = reference
        self.device_nodes = device_nodes

    @classmethod
    def from_config(cls, config: PeripheralOther):
        other = config.Other
        return cls(
            name=other.name,
            reference=other.reference,
            device_nodes=other.device_nodes,
        )
