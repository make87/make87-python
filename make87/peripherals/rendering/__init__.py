from typing import List, Optional

from make87.models import RenderingPeripheral as RenderingPeripheralModel
from make87.peripherals.base import PeripheralBase


class RenderingPeripheral(PeripheralBase):
    def __init__(
        self,
        name: str,
        supported_apis: List[str],
        device_nodes: List[str],
        max_performance: Optional[int] = None,
    ):
        super().__init__(name)
        self.supported_apis = supported_apis
        self.device_nodes = device_nodes
        self.max_performance = max_performance

    @classmethod
    def from_config(cls, config: RenderingPeripheralModel):
        rendering = config.Rendering
        return cls(
            name=rendering.name,
            supported_apis=rendering.supported_apis,
            device_nodes=rendering.device_nodes,
            max_performance=rendering.max_performance,
        )
