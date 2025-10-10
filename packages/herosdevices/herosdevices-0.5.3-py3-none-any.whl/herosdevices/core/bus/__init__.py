"""Module for representations of specific connection types, that can be used for interfacing hardware."""

from .onewire import OneWire
from .serial import SerialConnection
from .telnet import TelnetConnection

__all__ = ["OneWire", "SerialConnection", "TelnetConnection"]
