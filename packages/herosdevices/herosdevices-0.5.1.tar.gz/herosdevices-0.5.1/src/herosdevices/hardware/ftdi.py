"""Implements a wrapper for FT232H devices.

https://www.adafruit.com/product/2264

The implementation https://github.com/eblot/pyftdi supports simultaneous use of SPI and GPIO pins.
Unfortunately it is based on using bitmasks for everything.
"""

from enum import Enum
from types import TracebackType

from herosdevices.helper import log

try:
    from pyftdi import spi
except ImportError:
    log.exception("pyftdi not found, can't use ftdi devices!")


class GPIO(Enum):
    """Provide Rpi.GPIO like API."""

    IN = 0
    OUT = 1

    LOW = IN
    HIGH = OUT


class FT232H:
    """Provide pin wrapping and GPIO abstraction.

    see http://eblot.github.io/pyftdi/pinout.html

    The device sn is written to the eeprom of the Adafruit FT232H chips.
    To do that follow this description:
    https://cdn-learn.adafruit.com/downloads/pdf/adafruit-ft232h-breakout.pdf?timestamp=1550211653
    (section Erase EEPROM For Programming With FT_PROG)
    """

    PINMAP = {
        "D0": 0x0001,
        "D1": 0x0002,
        "D2": 0x0004,
        "D3": 0x0008,
        "D4": 0x0010,
        "D5": 0x0020,
        "D6": 0x0040,
        "D7": 0x0080,
        "C0": 0x0100,
        "C1": 0x0200,
        "C2": 0x0400,
        "C3": 0x0800,
        "C4": 0x1000,
        "C5": 0x2000,
        "C6": 0x4000,
        "C7": 0x8000,
    }

    def __init__(self, device_sn: str = "QAO201901") -> None:
        """Initialize SPI master."""
        self.device_sn = device_sn
        self.spi_master = spi.SpiController()

        # SPI master
        self.__enter__()

        # setup base gpio
        self._pin_state = 0x0000
        # C0 ... C3 as output, C4 ... C7 as input
        self.gpio = self.spi_master.get_gpio()
        for p in ["C4", "C5", "C6", "C7"]:
            self.gpio_set_input(pin=p)
        # for unknown reasons this does not work the other way around
        for p in ["C0", "C1", "C2", "C3"]:
            self.gpio_set_output(pin=p)

    def teardown(self) -> None:
        """Close down spi controller."""
        self.spi_master.terminate()

    def __enter__(self) -> None:
        """Configure spi controller on context manager enter."""
        self.spi_master.configure(f"ftdi://ftdi:232h:{self.device_sn}/1")

    def __exit__(
        self, type_: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        """Close down spi controller on exit."""
        self.teardown()

    def get_slave(self, cs: int = 0, freq: float = 12e6, mode: int = 0) -> int:
        """Get a slave aka. what you use to communicate.

        :param cs: chip-select 0 <= cs <= 4 (default CS0/ADBUS3/D3)
        :param freq: spi frequency (default 12MHz)
        :param mode: spi mode (default 0)
        :return: exposed spi slave
        """
        return self.spi_master.get_port(cs=cs, freq=freq, mode=mode)

    def gpio_setup(self, pin: str = "C0", mode: GPIO = GPIO.OUT, initial_value: GPIO = GPIO.LOW) -> None:
        """Set up a single GPIO pin.

        :param pin: name according to pinmap
        :param mode: GPIO.IN or GPIO.OUT
        :param initial_value: GPIO.LOW or GPIO.HIGH
        :return:
        """
        # pin bitmask
        bm_pin = self.PINMAP[pin]

        # mode bitmask
        if mode == GPIO.IN:
            bm_mode = 0x000
        else:
            bm_mode = self.PINMAP[pin]

        self.gpio.set_direction(bm_pin, bm_mode)

        # set value
        if mode == GPIO.OUT:
            self.gpio_write(pin, initial_value)

    def gpio_set_output(self, pin: str = "C0", initial_value: GPIO = GPIO.LOW) -> None:
        """Set one pin as output.

        :param pin: str pin descriptor
        :param initial_value: initial value default GPIO.LOW
        :return:
        """
        self.gpio_setup(pin, GPIO.OUT, initial_value)

    def gpio_set_input(self, pin: str = "C0", initial_value: GPIO = GPIO.LOW) -> None:  # noqa: ARG002
        """Set one pin as output.

        :param pin: str pin descriptor
        :param initial_value: initial value default GPIO.LOW (not used)
        :return:
        """
        self.gpio_setup(pin, GPIO.IN)

    def gpio_write(self, pin: str = "C0", value: GPIO = GPIO.LOW, write: bool = True) -> None:
        """Write pin level.

        :param pin:
        :param value:
        :return:
        """
        # value bitmap
        self._pin_state = (self._pin_state & (~self.PINMAP[pin])) | (self.PINMAP[pin] * value.value)

        if write:
            self.gpio_writeall()

    def gpio_writeall(self) -> None:
        """Write the configured pins to device."""
        self.gpio.write(self._pin_state)

    def gpio_read(self, pin: str = "C0") -> int:
        """Read gpio pin and report state."""
        return self.gpio.read() & self.PINMAP[pin]

    def setHigh(self, pin: str = "C0") -> None:  # noqa: N802
        """Deprecated alias for set_high."""  # noqa:D401
        log.warning("FT232H.setHigh() is deprecated, use FT232H.set_high() instead")
        self.set_high(pin)

    def set_high(self, pin: str = "C0") -> None:
        """Set a single pin to high."""
        self.gpio_set_output(pin, GPIO.HIGH)

    def setLow(self, pin: str = "C0") -> None:  # noqa: N802
        """Deprecated alias for set_low."""  # noqa:D401
        log.warning("FT232H.setHigh() is deprecated, use FT232H.set_high() instead")
        self.set_low(pin)

    def set_low(self, pin: str = "C0") -> None:
        """Set a single pin to low."""
        self.gpio_set_output(pin, GPIO.LOW)


if __name__ == "__main__":
    ftdi = FT232H()
    spi = ftdi.get_slave()
    import time

    for p in ["C1"] * 10:
        ftdi.setHigh(p)
        time.sleep(2)
        ftdi.setLow(p)
        time.sleep(2)
