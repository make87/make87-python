"""Intel RealSense camera peripheral implementation for Make87 hardware control.

This module provides the RealSenseCameraPeripheral class for managing Intel
RealSense camera devices in Make87 applications, including device identification,
model information, and device node access.
"""

from typing import List

from make87.models import RealSenseCameraPeripheral as RealSenseCameraPeripheralModel
from make87.peripherals.base import PeripheralBase


class RealSenseCameraPeripheral(PeripheralBase):
    """Intel RealSense camera peripheral device for Make87 hardware control.

    This class represents an Intel RealSense camera device in the Make87 system,
    providing access to depth and RGB camera functionality through device nodes
    and managing device-specific properties like serial number and model.

    Attributes:
        name: The name identifier for this RealSense camera peripheral
        device_nodes: List of device node paths for camera access
        serial_number: Unique serial number of the RealSense device
        model: RealSense camera model identifier
    """

    def __init__(
        self,
        name: str,
        device_nodes: List[str],
        serial_number: str,
        model: str,
    ):
        """Initialize the RealSense camera peripheral with device configuration.

        Args:
            name: The name identifier for this RealSense camera peripheral
            device_nodes: List of device node paths for camera access
                (e.g., ["/dev/video0", "/dev/video1"])
            serial_number: Unique serial number of the RealSense device
                for identification and configuration
            model: RealSense camera model identifier
                (e.g., "D435", "D455", "L515")

        Example:

            >>> realsense = RealSenseCameraPeripheral(
            ...     name="depth_camera",
            ...     device_nodes=["/dev/video0", "/dev/video1", "/dev/video2"],
            ...     serial_number="123456789012",
            ...     model="D435"
            ... )
        """
        super().__init__(name)
        self.device_nodes = device_nodes
        self.serial_number = serial_number
        self.model = model

    @classmethod
    def from_config(cls, config: RealSenseCameraPeripheralModel):
        """Create a RealSenseCameraPeripheral instance from configuration model.

        Factory method that creates a RealSenseCameraPeripheral instance from a
        RealSenseCameraPeripheralModel configuration object.

        Args:
            config: RealSenseCameraPeripheralModel configuration object

        Returns:
            RealSenseCameraPeripheral instance configured according to the model

        Example:

            >>> from make87.models import RealSenseCameraPeripheralModel
            >>> config = RealSenseCameraPeripheralModel(...)
            >>> realsense = RealSenseCameraPeripheral.from_config(config)
        """
        rs = config.RealSense
        return cls(
            name=rs.name,
            device_nodes=rs.device_nodes,
            serial_number=rs.serial_number,
            model=rs.model,
        )
