"""ISP peripheral implementation for Make87 hardware control.

This module provides the IspPeripheral class for managing Image Signal Processor
devices in Make87 applications, including feature detection and device node access.
"""

from typing import List

from make87.models import IspPeripheral as IspPeripheralModel
from make87.peripherals.base import PeripheralBase


class IspPeripheral(PeripheralBase):
    """ISP peripheral device for Make87 hardware control.

    This class represents an ISP (Image Signal Processor) device in the Make87
    system, providing access to image processing hardware through device nodes
    and managing supported ISP features.

    Attributes:
        name: The name identifier for this ISP peripheral
        supported_features: List of features supported by this ISP
        device_nodes: List of device node paths for ISP access
    """

    def __init__(
        self,
        name: str,
        supported_features: List[str],
        device_nodes: List[str],
    ):
        """Initialize the ISP peripheral with feature and device configuration.

        Args:
            name: The name identifier for this ISP peripheral
            supported_features: List of ISP features supported by this device
                (e.g., ["demosaic", "noise_reduction", "auto_white_balance"])
            device_nodes: List of device node paths for ISP access
                (e.g., ["/dev/v4l-subdev0"])

        Example:

            >>> isp = IspPeripheral(
            ...     name="main_isp",
            ...     supported_features=[
            ...         "demosaic",
            ...         "noise_reduction",
            ...         "auto_white_balance",
            ...         "auto_exposure"
            ...     ],
            ...     device_nodes=["/dev/v4l-subdev0", "/dev/v4l-subdev1"]
            ... )
        """
        super().__init__(name)
        self.supported_features = supported_features
        self.device_nodes = device_nodes

    @classmethod
    def from_config(cls, config: IspPeripheralModel):
        """Create an IspPeripheral instance from configuration model.

        Factory method that creates an IspPeripheral instance from an
        IspPeripheralModel configuration object.

        Args:
            config: IspPeripheralModel configuration object

        Returns:
            IspPeripheral instance configured according to the model

        Example:

            >>> from make87.models import IspPeripheralModel
            >>> config = IspPeripheralModel(...)
            >>> isp = IspPeripheral.from_config(config)
        """
        isp = config.ISP
        return cls(
            name=isp.name,
            supported_features=isp.supported_features,
            device_nodes=isp.device_nodes,
        )
