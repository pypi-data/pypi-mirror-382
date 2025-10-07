"""Module for devices like expansion boards or no-name sensors which are used with a Raspberry Pi."""

from .dhtxx import DHTxx
from .max318xx import MAX31855, MAX31865, c_v_d, c_v_d_quad
from .waveshare import WaveshareADS1256

__all__ = ["MAX31855", "MAX31865", "DHTxx", "WaveshareADS1256", "c_v_d", "c_v_d_quad"]
