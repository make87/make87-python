"""GPU peripheral implementation for Make87 hardware control.

This module provides the GpuPeripheral class for managing GPU devices
in Make87 applications, including device node access, model information,
and VRAM configuration.
"""

from typing import List, Optional

from make87.models import GpuPeripheral as GpuPeripheralModel
from make87.peripherals.base import PeripheralBase


class GpuPeripheral(PeripheralBase):
    """GPU peripheral device for Make87 hardware control.

    This class represents a GPU (Graphics Processing Unit) device in the Make87
    system, providing access to GPU hardware through device nodes and managing
    GPU-specific properties like model, index, and VRAM capacity.

    Attributes:
        name: The name identifier for this GPU peripheral
        model: The GPU model name or identifier
        device_nodes: List of device node paths for GPU access
        index: Optional GPU index for multi-GPU systems
        vram: Optional VRAM capacity in MB
    """

    def __init__(
        self,
        name: str,
        model: str,
        device_nodes: List[str],
        index: Optional[int] = None,
        vram: Optional[int] = None,
    ):
        """Initialize the GPU peripheral with device configuration.

        Args:
            name: The name identifier for this GPU peripheral
            model: The GPU model name or identifier (e.g., "RTX 4090", "Mali-G76")
            device_nodes: List of device node paths (e.g., ["/dev/dri/card0"])
            index: Optional GPU index for systems with multiple GPUs
            vram: Optional VRAM capacity in megabytes

        Example:

            >>> gpu = GpuPeripheral(
            ...     name="primary_gpu",
            ...     model="RTX 4090",
            ...     device_nodes=["/dev/dri/card0", "/dev/dri/renderD128"],
            ...     index=0,
            ...     vram=24576
            ... )
        """
        super().__init__(name)
        self.model = model
        self.device_nodes = device_nodes
        self.index = index
        self.vram = vram

    @classmethod
    def from_config(cls, config: GpuPeripheralModel):
        """Create a GpuPeripheral instance from configuration model.

        Factory method that creates a GpuPeripheral instance from a
        GpuPeripheralModel configuration object.

        Args:
            config: GpuPeripheralModel configuration object

        Returns:
            GpuPeripheral instance configured according to the model

        Example:

            >>> from make87.models import GpuPeripheralModel
            >>> config = GpuPeripheralModel(...)
            >>> gpu = GpuPeripheral.from_config(config)
        """
        gpu = config.GPU
        return cls(
            name=gpu.name,
            model=gpu.model,
            device_nodes=gpu.device_nodes,
            index=gpu.index,
            vram=gpu.vram,
        )
