from typing import List, Optional

from make87.models import GpioPeripheral as GpioPeripheralModel
from make87.peripherals.base import PeripheralBase


class GpioPeripheral(PeripheralBase):
    def __init__(
        self,
        chip_name: str,
        label: str,
        num_lines: int,
        device_nodes: List[str],
        lines: List[dict],
        name: Optional[str] = None,
    ):
        super().__init__(name or label)
        self.chip_name = chip_name
        self.label = label
        self.num_lines = num_lines
        self.device_nodes = device_nodes
        self.lines = lines

    @classmethod
    def from_config(cls, config: GpioPeripheralModel):
        gpio = config.GPIO
        return cls(
            chip_name=gpio.chip_name,
            label=gpio.label,
            num_lines=gpio.num_lines,
            device_nodes=gpio.device_nodes,
            lines=[line.model_dump() for line in gpio.lines],
            name=gpio.name,
        )
