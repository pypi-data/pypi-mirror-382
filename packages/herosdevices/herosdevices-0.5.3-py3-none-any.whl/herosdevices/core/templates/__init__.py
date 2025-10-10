"""A collection of templates for device drivers.

If implementing new hardware, e.g. developing new device drivers, it is encouraged to use a template class from this
module.
"""

from .acq_device import AcquisitionDeviceTemplate
from .camera import CameraTemplate
from .oscilloscope import OscilloscopeTemplate
from .serial import SerialDeviceTemplate
from .telnet import TelnetDeviceTemplate

__all__ = [
    "AcquisitionDeviceTemplate",
    "CameraTemplate",
    "OscilloscopeTemplate",
    "SerialDeviceTemplate",
    "TelnetDeviceTemplate",
]
