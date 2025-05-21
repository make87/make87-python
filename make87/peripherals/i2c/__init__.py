from typing import List

from make87.models.application_env_config import PeripheralI2C
from make87.peripherals.base import PeripheralBase


class I2cPeripheral(PeripheralBase):
    def __init__(
        self,
        name: str,
        bus_number: int,
        device_nodes: List[str],
        detected_devices: List[dict],
    ):
        super().__init__(name)
        self.bus_number = bus_number
        self.device_nodes = device_nodes
        self.detected_devices = detected_devices

    @classmethod
    def from_config(cls, config: PeripheralI2C):
        i2c = config.I2C
        return cls(
            name=i2c.name,
            bus_number=i2c.bus_number,
            device_nodes=i2c.device_nodes,
            detected_devices=[d.model_dump() for d in i2c.detected_devices],
        )
