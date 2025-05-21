from typing import overload

from make87.models import PeripheralCodec
from make87.models.application_env_config import (
    Peripheral,
    PeripheralCamera,
    PeripheralGenericDevice,
    PeripheralGpio,
    PeripheralGpu,
    PeripheralI2C,
    PeripheralIsp,
    PeripheralRealSense,
    PeripheralRendering,
)
from make87.peripherals.camera import CameraPeripheral
from make87.peripherals.generic_device import GenericDevicePeripheral
from make87.peripherals.gpu import GpuPeripheral
from make87.peripherals.i2c import I2cPeripheral
from make87.peripherals.gpio import GpioPeripheral
from make87.peripherals.codec import CodecPeripheral
from make87.peripherals.isp import IspPeripheral
from make87.peripherals.real_sense import RealSenseCameraPeripheral
from make87.peripherals.rendering import RenderingPeripheral
from make87.peripherals.other import OtherPeripheral


@overload
def create_peripheral_from_data(mp: PeripheralCamera) -> CameraPeripheral: ...
@overload
def create_peripheral_from_data(mp: PeripheralCodec) -> CodecPeripheral: ...
@overload
def create_peripheral_from_data(mp: PeripheralGenericDevice) -> GenericDevicePeripheral: ...
@overload
def create_peripheral_from_data(mp: PeripheralGpio) -> GpioPeripheral: ...
@overload
def create_peripheral_from_data(mp: PeripheralGpu) -> GpuPeripheral: ...
@overload
def create_peripheral_from_data(mp: PeripheralI2C) -> I2cPeripheral: ...
@overload
def create_peripheral_from_data(mp: PeripheralIsp) -> IspPeripheral: ...
@overload
def create_peripheral_from_data(mp: PeripheralRealSense) -> RealSenseCameraPeripheral: ...
@overload
def create_peripheral_from_data(mp: PeripheralRendering) -> RenderingPeripheral: ...
@overload
def create_peripheral_from_data(mp: object) -> OtherPeripheral: ...


def create_peripheral_from_data(mp) -> Peripheral:
    if isinstance(mp, PeripheralCamera):
        return CameraPeripheral.from_config(mp)
    elif isinstance(mp, PeripheralCodec):
        return CodecPeripheral.from_config(mp)
    elif isinstance(mp, PeripheralGenericDevice):
        return GenericDevicePeripheral.from_config(mp)
    elif isinstance(mp, PeripheralGpio):
        return GpioPeripheral.from_config(mp)
    elif isinstance(mp, PeripheralGpu):
        return GpuPeripheral.from_config(mp)
    elif isinstance(mp, PeripheralI2C):
        return I2cPeripheral.from_config(mp)
    elif isinstance(mp, PeripheralIsp):
        return IspPeripheral.from_config(mp)
    elif isinstance(mp, PeripheralRealSense):
        return RealSenseCameraPeripheral.from_config(mp)
    elif isinstance(mp, PeripheralRendering):
        return RenderingPeripheral.from_config(mp)
    else:  # ("Other", "Speaker", "Keyboard", "Mouse")
        return OtherPeripheral.from_config(mp)
