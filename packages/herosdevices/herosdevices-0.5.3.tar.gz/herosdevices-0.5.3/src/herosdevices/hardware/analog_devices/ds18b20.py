"""Module for ds18b20 temperature sensor probe representations."""

from herosdevices.core.bus import OneWire


class DS18B20(OneWire):
    """One wire temperature sensor type DS18B20."""

    _observables = [("temperature", float, "mdegC")]
