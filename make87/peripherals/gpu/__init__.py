from typing import List, Optional

from make87.models.application_env_config import PeripheralGpu
from make87.peripherals.base import PeripheralBase


class GpuPeripheral(PeripheralBase):
    def __init__(
        self,
        name: str,
        model: str,
        device_nodes: List[str],
        index: Optional[int] = None,
        vram: Optional[int] = None,
    ):
        super().__init__(name)
        self.model = model
        self.device_nodes = device_nodes
        self.index = index
        self.vram = vram

    @classmethod
    def from_config(cls, config: PeripheralGpu):
        gpu = config.GPU
        return cls(
            name=gpu.name,
            model=gpu.model,
            device_nodes=gpu.device_nodes,
            index=gpu.index,
            vram=gpu.vram,
        )
