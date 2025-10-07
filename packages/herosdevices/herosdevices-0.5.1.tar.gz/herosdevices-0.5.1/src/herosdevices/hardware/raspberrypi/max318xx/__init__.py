"""Module for MAX318xx thermocouple amplifiers representations."""

from .max31855 import MAX31855
from .max31865 import MAX31865, c_v_d, c_v_d_quad

# TODO: all these should be moved to hardware/analog_devices

__all__ = ["MAX31855", "MAX31865", "c_v_d", "c_v_d_quad"]
