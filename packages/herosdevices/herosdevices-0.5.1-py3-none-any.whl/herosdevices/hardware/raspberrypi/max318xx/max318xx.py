"""
Implements the MAX31865 resistance-to-digital converter interface.

The MAX31865 chip communicates via SPI, and in this implementation, SPI communication
is carried out through bit-banging using the RPi.GPIO library. For better performance,
using an SPI library such as spidev is recommended, but this code is a first approach.

Note: numpy is only required if implementing the full Calendar-Van Dusen equations.

This code is adapted from steve71's work: https://github.com/steve71/MAX31865
"""

# system packages
from abc import abstractmethod

from herosdevices.helper import log

# rpi specific imports
try:
    from RPi import GPIO
except ImportError:
    log.warning("could not import RPi.GPIO")

from herosdevices.helper import log


class FaultError(Exception):
    """Exception class for handling faults detected in the RTD or wiring."""


class MAX318xx:
    """Base class for MAX318xx series resistance-to-digital converters.

    Handles SPI communication via bit-banging using GPIO pins.

    Attributes:
        cs_pin (dict): {"description": "Chip select GPIO pin number"}.
        miso_pin (int): Master In Slave Out GPIO pin number.
        mosi_pin (int): Master Out Slave In GPIO pin number.
        clk_pin (int): Clock GPIO pin number.
    """

    def __init__(self, cs_pins: dict, miso_pin: int = 9, mosi_pin: int | None = 10, clk_pin: int = 11) -> None:
        """Initialize MAX318xx object with specified GPIO pins and sets up GPIO.

        Args:
            cs_pin (dict): {"description": "Chip select GPIO pin number"}.
            miso_pin (int): GPIO pin for MISO.
            mosi_pin (int): GPIO pin for MOSI.
            clk_pin (int): GPIO pin for clock.
        """
        # SPI specific
        self.cs_pins = cs_pins
        self.miso_pin = miso_pin
        self.mosi_pin = mosi_pin
        self.clk_pin = clk_pin
        log.debug(f"CS: {self.cs_pins}\tMISO: {self.miso_pin}\tMOSI: {self.mosi_pin}\tCLK: {self.clk_pin}")
        log.debug(f"CS: {self.cs_pins}\tMISO: {self.miso_pin}\tMOSI: {self.mosi_pin}\tCLK: {self.clk_pin}")
        self._setup_gpio()

    def _setup_gpio(self) -> None:
        """Configure GPIO pins for SPI communication."""
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for cs_pin in self.cs_pins.values():
            GPIO.setup(cs_pin, GPIO.OUT)
            GPIO.output(cs_pin, GPIO.HIGH)
        GPIO.setup(self.miso_pin, GPIO.IN)
        GPIO.setup(self.clk_pin, GPIO.OUT)
        GPIO.output(self.clk_pin, GPIO.LOW)
        if self.mosi_pin is not None:
            GPIO.setup(self.mosi_pin, GPIO.OUT)
            GPIO.output(self.mosi_pin, GPIO.LOW)

    def write_register(self, reg_num: int, data_byte: int) -> None:
        """Write a byte to a specified register.

        Args:
            regNum (int): Register number to write to.
            dataByte (int): Data byte to write.
        """
        GPIO.output(self.cs_pins, GPIO.LOW)  # TODO: self.cs_pins is a dict but this needs a single int...
        GPIO.output(self.cs_pins, GPIO.LOW)
        # 0x8x to specify 'write register value'
        address_byte = 0x80 | reg_num
        # first byte is address byte
        self.send_byte(address_byte)
        # the rest are data bytes
        self.send_byte(data_byte)
        GPIO.output(self.cs_pins, GPIO.HIGH)
        GPIO.output(self.cs_pins, GPIO.HIGH)

    def read_register(self, cs_pin: int, num_registers: int, reg_num_start: int | None = None) -> list[int]:
        """Read one or more bytes starting from a specified register.

        Args:
            cs_pin (int): Chip select GPIO pin number.
            numRegisters (int): Number of bytes to read.
            regNumStart (int, optional): Starting register number for the read operation.

        Returns:
            list: List of bytes read from the device.
        """
        out = []
        GPIO.output(cs_pin, GPIO.LOW)
        GPIO.output(cs_pin, GPIO.LOW)
        # 0x to specify 'read register value'
        if self.mosi_pin is not None:
            # TODO: this can be none, add doc that required if mosi_pin is not None
            self.send_byte(reg_num_start)
        for _ in range(num_registers):
            data = self.recv_byte()
            out.append(data)
        GPIO.output(cs_pin, GPIO.HIGH)
        GPIO.output(cs_pin, GPIO.HIGH)
        return out

    def send_byte(self, byte: int) -> None:
        """Send a byte via SPI by bit-banging.

        Args:
            byte (int): Byte value to send.
        """
        for _ in range(8):
            GPIO.output(self.clk_pin, GPIO.HIGH)
            if byte & 0x80:
                GPIO.output(self.mosi_pin, GPIO.HIGH)
            else:
                GPIO.output(self.mosi_pin, GPIO.LOW)
            byte <<= 1
            GPIO.output(self.clk_pin, GPIO.LOW)

    def recv_byte(self) -> int:
        """Receive a byte via SPI by bit-banging.

        Returns:
            int: Byte received.
        """
        byte = 0x00
        for _ in range(8):
            GPIO.output(self.clk_pin, GPIO.HIGH)
            byte <<= 1
            if GPIO.input(self.miso_pin):
                byte |= 0x1
            GPIO.output(self.clk_pin, GPIO.LOW)
        return byte

    def create_dict(self, values: list[float], observable: str, unit: str) -> dict:
        """Build dictionary of observables to be returned by the sensor."""  # TODO: better docstring
        if len(values) != len(self.cs_pins):
            raise RuntimeWarning("Sensorlist length does not match number of measured values")
        description = [key + f"_{observable}" for key in self.cs_pins]
        return {f"{key}": (val, unit) for key, val in zip(description, values, strict=True)}

    @abstractmethod
    def _observable_data(self) -> dict:
        """Abstract method to check if new data is available.

        This method should be implemented in subclasses.

        Raises:
            NotImplementedError: If not implemented in subclass.

        returnstyle: {"data_name": (data, "Unit")}
        """
