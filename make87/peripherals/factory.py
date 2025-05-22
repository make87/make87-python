from typing import overload

from make87.models import (
    Peripheral,
    CodecPeripheral as CodecPeripheralModel,
    CameraPeripheral as CameraPeripheralModel,
    GenericDevicePeripheral as GenericDevicePeripheralModel,
    GpioPeripheral as GpioPeripheralModel,
    GpuPeripheral as GpuPeripheralModel,
    I2cPeripheral as I2cPeripheralModel,
    IspPeripheral as IspPeripheralModel,
    RealSenseCameraPeripheral as RealSenseCameraPeripheralModel,
    RenderingPeripheral as RenderingPeripheralModel,
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
def create_peripheral_from_data(mp: CameraPeripheralModel) -> CameraPeripheral: ...
@overload
def create_peripheral_from_data(mp: CodecPeripheralModel) -> CodecPeripheral: ...
@overload
def create_peripheral_from_data(mp: GenericDevicePeripheralModel) -> GenericDevicePeripheral: ...
@overload
def create_peripheral_from_data(mp: GpioPeripheralModel) -> GpioPeripheral: ...
@overload
def create_peripheral_from_data(mp: GpuPeripheralModel) -> GpuPeripheral: ...
@overload
def create_peripheral_from_data(mp: I2cPeripheralModel) -> I2cPeripheral: ...
@overload
def create_peripheral_from_data(mp: IspPeripheralModel) -> IspPeripheral: ...
@overload
def create_peripheral_from_data(mp: RealSenseCameraPeripheralModel) -> RealSenseCameraPeripheral: ...
@overload
def create_peripheral_from_data(mp: RenderingPeripheralModel) -> RenderingPeripheral: ...
@overload
def create_peripheral_from_data(mp: object) -> OtherPeripheral: ...


def create_peripheral_from_data(mp) -> Peripheral:
    if isinstance(mp, CameraPeripheralModel):
        return CameraPeripheral.from_config(mp)
    elif isinstance(mp, CodecPeripheralModel):
        return CodecPeripheral.from_config(mp)
    elif isinstance(mp, GenericDevicePeripheralModel):
        return GenericDevicePeripheral.from_config(mp)
    elif isinstance(mp, GpioPeripheralModel):
        return GpioPeripheral.from_config(mp)
    elif isinstance(mp, GpuPeripheralModel):
        return GpuPeripheral.from_config(mp)
    elif isinstance(mp, I2cPeripheralModel):
        return I2cPeripheral.from_config(mp)
    elif isinstance(mp, IspPeripheralModel):
        return IspPeripheral.from_config(mp)
    elif isinstance(mp, RealSenseCameraPeripheralModel):
        return RealSenseCameraPeripheral.from_config(mp)
    elif isinstance(mp, RenderingPeripheralModel):
        return RenderingPeripheral.from_config(mp)
    else:  # ("Other", "Speaker", "Keyboard", "Mouse")
        return OtherPeripheral.from_config(mp)
