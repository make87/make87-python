from typing import List

from make87.models import IspPeripheral as IspPeripheralModel
from make87.peripherals.base import PeripheralBase


class IspPeripheral(PeripheralBase):
    def __init__(
        self,
        name: str,
        supported_features: List[str],
        device_nodes: List[str],
    ):
        super().__init__(name)
        self.supported_features = supported_features
        self.device_nodes = device_nodes

    @classmethod
    def from_config(cls, config: IspPeripheralModel):
        isp = config.ISP
        return cls(
            name=isp.name,
            supported_features=isp.supported_features,
            device_nodes=isp.device_nodes,
        )
