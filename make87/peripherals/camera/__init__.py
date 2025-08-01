"""Camera peripheral implementation for Make87 hardware control.

This module provides the CameraPeripheral class for managing camera devices
in Make87 applications, including device node access, protocol configuration,
and volume mounting for camera hardware.
"""

from typing import List, Optional

from make87.models import CameraPeripheral as CameraPeripheralModel
from make87.peripherals.base import PeripheralBase


class CameraPeripheral(PeripheralBase):
    """Camera peripheral device for Make87 hardware control.

    This class represents a camera device in the Make87 system, providing
    access to camera hardware through device nodes and supporting various
    camera types and protocols.

    Attributes:
        name: The name identifier for this camera peripheral
        device_nodes: List of device node paths for camera access
        reference: Reference identifier for the camera
        volumes: List of volume mount configurations
        camera_type: Optional camera type specification
        protocol: Optional protocol specification for camera communication
    """

    def __init__(
        self,
        name: str,
        device_nodes: List[str],
        reference: str,
        volumes: List[List[str]],
        camera_type: Optional[str] = None,
        protocol: Optional[str] = None,
    ):
        """Initialize the camera peripheral with device configuration.

        Args:
            name: The name identifier for this camera peripheral
            device_nodes: List of device node paths (e.g., ["/dev/video0"])
            reference: Reference identifier for the camera
            volumes: List of volume mount configurations for the camera
            camera_type: Optional camera type (e.g., "USB", "CSI")
            protocol: Optional protocol specification (e.g., "V4L2", "GStreamer")

        Example:

            >>> camera = CameraPeripheral(
            ...     name="main_camera",
            ...     device_nodes=["/dev/video0"],
            ...     reference="camera_ref_001",
            ...     volumes=[["/host/camera", "/camera"]],
            ...     camera_type="USB",
            ...     protocol="V4L2"
            ... )
        """
        super().__init__(name)
        self.device_nodes = device_nodes
        self.reference = reference
        self.volumes = volumes
        self.camera_type = camera_type
        self.protocol = protocol

    @classmethod
    def from_config(cls, config: CameraPeripheralModel):
        """Create a CameraPeripheral instance from configuration model.

        Factory method that creates a CameraPeripheral instance from a
        CameraPeripheralModel configuration object.

        Args:
            config: CameraPeripheralModel configuration object

        Returns:
            CameraPeripheral instance configured according to the model

        Example:

            >>> from make87.models import CameraPeripheralModel
            >>> config = CameraPeripheralModel(...)
            >>> camera = CameraPeripheral.from_config(config)
        """
        camera = config.Camera  # CameraPeripheral instance
        return cls(
            name=camera.name,
            device_nodes=camera.device_nodes,
            reference=camera.reference,
            volumes=camera.volumes,
            camera_type=camera.camera_type,
            protocol=camera.protocol,
        )
