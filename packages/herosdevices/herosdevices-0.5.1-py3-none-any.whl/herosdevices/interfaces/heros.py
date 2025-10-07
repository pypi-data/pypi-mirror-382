"""Interfaces for devices which define capabilities that should be published via heros."""

from . import Interface


class ConfiguredDevice(Interface):
    """Base interface for heros devices."""

    _hero_implements = ["herosdevices.interfaces.ConfiguredDevice"]
    _hero_methods = ["get_configuration", "set_configuration", "get_status"]
