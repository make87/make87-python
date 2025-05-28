from typing import List

from make87.models import RealSenseCameraPeripheral as RealSenseCameraPeripheralModel
from make87.peripherals.base import PeripheralBase


class RealSenseCameraPeripheral(PeripheralBase):
    def __init__(
        self,
        name: str,
        device_nodes: List[str],
        serial_number: str,
        model: str,
    ):
        super().__init__(name)
        self.device_nodes = device_nodes
        self.serial_number = serial_number
        self.model = model

    @classmethod
    def from_config(cls, config: RealSenseCameraPeripheralModel):
        rs = config.RealSense
        return cls(
            name=rs.name,
            device_nodes=rs.device_nodes,
            serial_number=rs.serial_number,
            model=rs.model,
        )
