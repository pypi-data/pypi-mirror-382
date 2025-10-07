"""MAX31865 Resistance to Digital Converter.

This module implements an interface for the MAX31865 resistance temperature detector (RTD) converter.
The chip communicates over SPI. This implementation uses GPIO bit-banging on a Raspberry Pi.
Using spidev would be more efficient, but initial attempts with spidev were unsuccessful.

This code is based on the work of steve71: https://github.com/steve71/MAX31865

Classes:
- MAX31865: Provides methods to read resistance and temperature from PT100/PT1000 sensors.
  - Initialization allows configuration of SPI pins, reference resistance, and wiring type.
  - Methods to fetch resistance, convert resistance to temperature, and handle errors.

Usage:
- Instantiate multiple sensor objects for different chip select pins.
- Loop to read and print temperature readings.
- Gracefully handle interruption and clean GPIO resources.

Notes:
- Proper wiring and pull-down resistors are essential.
- Optimized for use with a Raspberry Pi and RPi.GPIO.
"""

# system packages
import math
import time
from collections.abc import Callable

import numpy as np

from herosdevices.helper import log

from .max318xx import FaultError, MAX318xx

# IEC 751 coefficients for temperature calculations
A = 3.908e-3
B = -5.775e-7
C = -4.183e-12


def c_v_d(r: float, r_0: float) -> float:
    """Calculate temperature using Callendar-Van Dusen equation.

    This function converts resistance to temperature based on the Calendar-Van Dusen
    equation, which relates resistance in Ohms to temperature in Celsius. It uses numpy
    for polynomial root solving.

    Args:
        r (float): Resistance in Ohms.
        r_0 (float): Resistance at 0°C in Ohms.

    Returns:
        float: Estimated temperature in degrees Celsius.

    Raises:
        ImportError: If numpy is not installed.
        ValueError: If the polynomial root calculation encounters issues (e.g., negative discriminant).
    """
    coefficients = np.array([r_0 - r, r_0 * A, r_0 * B, -100.0 * r_0 * C, r_0 * C])
    roots = np.roots(coefficients[::-1])
    theta = roots[-1]
    return abs(theta)


def c_v_d_quad(r: float, r_0: float) -> float:
    """Approximate temperature using a quadratic form of the Callendar-Van Dusen equation.

    This method offers a fast and reasonably accurate way to estimate temperature
    from resistance, suitable for class A PT100 sensors with about 0.2°C accuracy.

    Args:
        r (float): Resistance in Ohms.
        r_0 (float): Resistance at 0°C in Ohms.

    Returns:
        float: Estimated temperature in degrees Celsius.

    Raises:
        ValueError: If the discriminant in the quadratic formula is negative.
    """
    discriminant = (r_0 * A) ** 2 - 4.0 * r_0 * B * (r_0 - r)
    if discriminant < 0:
        raise ValueError("Negative discriminant in quadratic solution.")
    return (-r_0 * A + math.sqrt(discriminant)) / (2 * r_0 * B)


class MAX31865(MAX318xx):
    """
    Interface class for MAX31865 resistance temperature sensor.

    Args:
        cs_pin (int): Chip select GPIO pin (default: 8).
        miso_pin (int): MISO GPIO pin (default: 9).
        mosi_pin (int): MOSI GPIO pin (default: 10).
        clk_pin (int): Clock GPIO pin (default: 11).
        r_0 (float): Resistance at 0°C, in Ohms (default: 1000 for PT1000).
        r_ref (float): Reference resistor resistance, in Ohms (default: 400).
        three_wire (bool): Use 3-wire configuration (default: False).
        log (logging.Logger): Optional logger for debug messages.
    """

    def __init__(
        self,
        cs_pin: int = 8,
        miso_pin: int = 9,
        mosi_pin: int = 10,
        clk_pin: int = 11,
        r_0: float = 1e3,
        r_ref: float = 4e2,
        three_wire: bool = False,
    ) -> None:
        """
        Initialize MAX31865 sensor interface.

        Args:
            cs_pin (int): Chip select GPIO pin.
            miso_pin (int): MISO GPIO pin.
            mosi_pin (int): MOSI GPIO pin.
            clk_pin (int): Clock GPIO pin.
            r_0 (float): Resistance at 0°C, default 1000 Ohms.
            r_ref (float): Reference resistor value.
            three_wire (bool): True for 3-wire configuration.
            log (logging.Logger): Optional logger.
        """
        # TODO: this can not work, it takes a dict for cs_pin, not an int
        super().__init__(cs_pins=cs_pin, miso_pin=miso_pin, mosi_pin=mosi_pin, clk_pin=clk_pin)
        self.r_ref = r_ref
        self.r_0 = r_0
        log.debug(f"PT resistance: {self.r_0} Ohm, Reference: {self.r_ref} Ohm")
        # Configuration byte: One-shot or continuous settings, wire type
        self.config = 0b10100010 if not three_wire else 0b10110010
        log.debug(f"Three-wire setup: {three_wire}")

    def _raise_for_fault(self, out: list) -> None:
        """Raise fault exceptions based on status register bits.

        10 Mohm resistor is on breakout board to help
        detect cable faults
        bit 7: RTD High Threshold / cable fault open
        bit 6: RTD Low Threshold / cable fault short
        bit 5: REFIN- > 0.85 x VBias -> must be requested
        bit 4: REFIN- < 0.85 x VBias (FORCE- open) -> must be requested
        bit 3: RTDIN- < 0.85 x VBias (FORCE- open) -> must be requested
        bit 2: Overvoltage / undervoltage fault
        bits 1,0 don't care

        Args:
            out (list): Data read from sensor registers.

        Raises:
            FaultError: When faults such as open circuit or short circuit are detected.
        """
        [hft_msb, hft_lsb] = [out[3], out[4]]
        hft = ((hft_msb << 8) | hft_lsb) >> 1
        log.spam(f"High fault threshold: {hft:d}")
        [lft_msb, lft_lsb] = [out[5], out[6]]
        lft = ((lft_msb << 8) | lft_lsb) >> 1
        log.spam(f"Low fault threshold: {lft:d}")
        status = out[7]
        log.spam(f"Status byte: {status:x}")
        if status & 0x80:
            raise FaultError("High threshold limit reached (possible cable fault/open)")
        if status & 0x40:
            raise FaultError("Low threshold limit reached (possible short circuit)")
        if status & 0x04:
            raise FaultError("Overvoltage or undervoltage detected")

    def read_resistance(self, cs_pin: int) -> float:
        """Initiate resistance measurement and return resistance value.

        Returns:
            float: Resistance in Ohms.
        """
        self.write_register(0, self.config)
        time.sleep(0.1)
        out = self.read_register(cs_pin, 8, 0)
        conf_reg = out[0]
        log.spam(f"Configuration register: {conf_reg:x}")
        [rtd_msb, rtd_lsb] = [out[1], out[2]]
        rtd_adc_code = ((rtd_msb << 8) | rtd_lsb) >> 1
        resistance = (rtd_adc_code * self.r_ref) / 2**15
        log.debug(f"Resistance: {resistance:.3f} Ohm")
        self._raise_for_fault(out)
        return resistance

    def read_temp(self, convert: Callable[[float, float], float] = c_v_d_quad) -> dict:
        """Read resistance and convert to temperature.

        Args:
            convert (function): Function to convert resistance to temperature.
                Defaults to c_v_d_quad.

        Returns:
            float: Temperature in Celsius.
        """
        return self._observable_data(convert)["temperature"]  # TODO: This calls the event. Is this what we want here?

    def _observable_data(self, convert: Callable[[float, float], float] = c_v_d_quad) -> dict:
        """Fetch fresh resistance and temperature data.

        Args:
            convert (function): Conversion function from resistance to temperature.

        Returns:
            dict: Dictionary with resistance and temperature.
        """
        log.spam(f"Using conversion method: {convert!r}")
        resistance_values = [self.read_resistance(cs_pin) for cs_pin in self.cs_pins]
        temperature_values = [convert(val, self.r_0) for val in resistance_values]
        res_dict = self.create_dict(resistance_values, "resistance", "Ohm")
        temp_dict = self.create_dict(temperature_values, "temperature", "degC")
        return {**res_dict, **temp_dict}
