"""Drivers for the DHT11 and DHT22 temperature/humidity sensors."""

from typing import Literal

import adafruit_dht  # type: ignore
import board  # type: ignore

from herosdevices.helper import log


class DHTxx:
    """Class to support reading temperatures and humidities from the DHT11 and DHT22 onewire sensors.

    This class builds on the "Adafruit_DHT" python package.
    """

    def __init__(self, device: Literal[11, 22] = 22, pin_name: int | str = 4) -> None:
        """Create a new DHTxx representation.

        Args:
            device: type of the device. Must be either 11 for a DHT11 or 22 for a DHT22.
            pin_name: number of the pin, the sensor is connected to.
        """
        assert device in [11, 22], "Cannot handle other devices then DHT22 and DHT11"
        if isinstance(pin_name, int) or (isinstance(pin_name, str) and pin_name.isdigit()):
            pin_name = f"D{pin_name}"

        self.device = device
        self.pin = getattr(board, pin_name)
        if device == 22:  # noqa: PLR2004
            self.dht_device = adafruit_dht.DHT22(self.pin)
        else:
            self.dht_device = adafruit_dht.DHT11(self.pin)

    def _observable_data(self) -> dict[str, tuple[float, str]] | None:
        try:
            temperature = self.dht_device.temperature
            humidity = self.dht_device.humidity
        except Exception:  # noqa: BLE001
            log.warning("Error converting data from DHTxx sensor", exc_info=True)
            return None
        return {"temperature": (temperature, "degC"), "humidity": (humidity, "pct")}
