"""Rendering peripheral implementation for Make87 hardware control.

This module provides the RenderingPeripheral class for managing rendering
devices in Make87 applications, including graphics API support, performance
configuration, and device node access.
"""

from typing import List, Optional

from make87.models import RenderingPeripheral as RenderingPeripheralModel
from make87.peripherals.base import PeripheralBase


class RenderingPeripheral(PeripheralBase):
    """Rendering peripheral device for Make87 hardware control.

    This class represents a rendering device in the Make87 system, providing
    access to graphics rendering hardware through device nodes and managing
    supported graphics APIs and performance characteristics.

    Attributes:
        name: The name identifier for this rendering peripheral
        supported_apis: List of graphics APIs supported by this device
        device_nodes: List of device node paths for rendering access
        max_performance: Optional maximum performance rating or score
    """

    def __init__(
        self,
        name: str,
        supported_apis: List[str],
        device_nodes: List[str],
        max_performance: Optional[int] = None,
    ):
        """Initialize the rendering peripheral with device configuration.

        Args:
            name: The name identifier for this rendering peripheral
            supported_apis: List of graphics APIs supported by this device
                (e.g., ["OpenGL", "Vulkan", "OpenCL", "CUDA"])
            device_nodes: List of device node paths for rendering access
                (e.g., ["/dev/dri/card0", "/dev/nvidia0"])
            max_performance: Optional maximum performance rating or benchmark score
                for the rendering device

        Example:

            >>> rendering = RenderingPeripheral(
            ...     name="graphics_card",
            ...     supported_apis=["OpenGL", "Vulkan", "CUDA"],
            ...     device_nodes=["/dev/dri/card0", "/dev/nvidia0"],
            ...     max_performance=15000
            ... )
        """
        super().__init__(name)
        self.supported_apis = supported_apis
        self.device_nodes = device_nodes
        self.max_performance = max_performance

    @classmethod
    def from_config(cls, config: RenderingPeripheralModel):
        """Create a RenderingPeripheral instance from configuration model.

        Factory method that creates a RenderingPeripheral instance from a
        RenderingPeripheralModel configuration object.

        Args:
            config: RenderingPeripheralModel configuration object

        Returns:
            RenderingPeripheral instance configured according to the model

        Example:

            >>> from make87.models import RenderingPeripheralModel
            >>> config = RenderingPeripheralModel(...)
            >>> rendering = RenderingPeripheral.from_config(config)
        """
        rendering = config.Rendering
        return cls(
            name=rendering.name,
            supported_apis=rendering.supported_apis,
            device_nodes=rendering.device_nodes,
            max_performance=rendering.max_performance,
        )
