from typing import List

from make87.models import CodecPeripheral as CodecPeripheralModel
from make87.peripherals.base import PeripheralBase


class CodecPeripheral(PeripheralBase):
    def __init__(
        self,
        name: str,
        supported_codecs: List[str],
        device_nodes: List[str],
    ):
        super().__init__(name)
        self.supported_codecs = supported_codecs
        self.device_nodes = device_nodes

    @classmethod
    def from_config(cls, config: CodecPeripheralModel):
        codec = config.Codec
        return cls(
            name=codec.name,
            supported_codecs=codec.supported_codecs,
            device_nodes=codec.device_nodes,
        )
