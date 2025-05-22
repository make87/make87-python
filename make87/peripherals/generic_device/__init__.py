from make87.models import GenericDevicePeripheral as GenericDevicePeripheralModel
from make87.peripherals.base import PeripheralBase


class GenericDevicePeripheral(PeripheralBase):
    def __init__(self, name: str, device_node: str):
        super().__init__(name)
        self.device_node = device_node

    @classmethod
    def from_config(cls, config: GenericDevicePeripheralModel):
        generic = config.GenericDevice
        return cls(
            name=generic.name,
            device_node=generic.device_node,
        )
