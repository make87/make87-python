from typing import List, Optional

from make87.models import CameraPeripheral as CameraPeripheralModel
from make87.peripherals.base import PeripheralBase


class CameraPeripheral(PeripheralBase):
    def __init__(
        self,
        name: str,
        device_nodes: List[str],
        reference: str,
        volumes: List[List[str]],
        camera_type: Optional[str] = None,
        protocol: Optional[str] = None,
    ):
        super().__init__(name)
        self.device_nodes = device_nodes
        self.reference = reference
        self.volumes = volumes
        self.camera_type = camera_type
        self.protocol = protocol

    @classmethod
    def from_config(cls, config: CameraPeripheralModel):
        camera = config.Camera  # CameraPeripheral instance
        return cls(
            name=camera.name,
            device_nodes=camera.device_nodes,
            reference=camera.reference,
            volumes=camera.volumes,
            camera_type=camera.camera_type,
            protocol=camera.protocol,
        )
