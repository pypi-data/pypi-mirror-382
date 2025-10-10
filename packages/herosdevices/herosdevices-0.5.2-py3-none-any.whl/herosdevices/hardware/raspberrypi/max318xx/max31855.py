"""Uses Superclass MAX318xx for communication methods and implements MAX31855 specific functions."""

# system packages
import math
from collections.abc import Callable

from herosdevices.helper import log

from .max318xx import MAX318xx


def temperature_NIST(t_remote: float, t_ambient: float) -> float:  # noqa: N802
    """Correct temperature for ambient effects according to the Adafruit library.

    https://github.com/adafruit/Adafruit_CircuitPython_MAX31855/blob/main/adafruit_max31855.py
    This function applies a correction to the remote thermocouple temperature reading based
    on the ambient temperature, using the polynomial approximations from the Adafruit MAX31855
    library.

    Args:
        t_remote (float): The remote thermocouple junction temperature in Celsius.
        t_ambient (float): The ambient (cold junction) temperature in Celsius.

    Returns:
        float: Corrected temperature in Celsius.

    Raises:
        RuntimeError: If the total thermoelectric voltage is out of the expected range.
    """
    # temperature of remote thermocouple junction
    tr = t_remote
    # temperature of device (cold junction)
    t_amb = t_ambient
    # thermocouple voltage based on MAX31855's uV/degC for type K (table 1)
    v_out = 0.041276 * (tr - t_amb)
    # cold junction equivalent thermocouple voltage
    if t_amb >= 0:
        v_ref = (
            -0.176004136860e-01
            + 0.389212049750e-01 * t_amb
            + 0.185587700320e-04 * math.pow(t_amb, 2)
            + -0.994575928740e-07 * math.pow(t_amb, 3)
            + 0.318409457190e-09 * math.pow(t_amb, 4)
            + -0.560728448890e-12 * math.pow(t_amb, 5)
            + 0.560750590590e-15 * math.pow(t_amb, 6)
            + -0.320207200030e-18 * math.pow(t_amb, 7)
            + 0.971511471520e-22 * math.pow(t_amb, 8)
            + -0.121047212750e-25 * math.pow(t_amb, 9)
            + 0.1185976 * math.exp(-0.1183432e-03 * math.pow(t_amb - 0.1269686e03, 2))
        )
    else:
        v_ref = (
            0.394501280250e-01 * t_amb
            + 0.236223735980e-04 * math.pow(t_amb, 2)
            + -0.328589067840e-06 * math.pow(t_amb, 3)
            + -0.499048287770e-08 * math.pow(t_amb, 4)
            + -0.675090591730e-10 * math.pow(t_amb, 5)
            + -0.574103274280e-12 * math.pow(t_amb, 6)
            + -0.310888728940e-14 * math.pow(t_amb, 7)
            + -0.104516093650e-16 * math.pow(t_amb, 8)
            + -0.198892668780e-19 * math.pow(t_amb, 9)
            + -0.163226974860e-22 * math.pow(t_amb, 10)
        )
    # total thermoelectric voltage
    v_total = v_out + v_ref
    # determine coefficients
    # https://srdata.nist.gov/its90/type_k/kcoefficients_inverse.html
    if -5.891 <= v_total <= 0:  # noqa: PLR2004
        d_coef = (
            0.0000000e00,
            2.5173462e01,
            -1.1662878e00,
            -1.0833638e00,
            -8.9773540e-01,
            -3.7342377e-01,
            -8.6632643e-02,
            -1.0450598e-02,
            -5.1920577e-04,
        )
    elif 0 < v_total <= 20.644:  # noqa: PLR2004
        d_coef = (
            0.000000e00,
            2.508355e01,
            7.860106e-02,
            -2.503131e-01,
            8.315270e-02,
            -1.228034e-02,
            9.804036e-04,
            -4.413030e-05,
            1.057734e-06,
            -1.052755e-08,
        )
    elif 20.644 < v_total <= 54.886:  # noqa: PLR2004
        d_coef = (
            -1.318058e02,
            4.830222e01,
            -1.646031e00,
            5.464731e-02,
            -9.650715e-04,
            8.802193e-06,
            -3.110810e-08,
        )
    else:
        msg = f"total thermoelectric voltage out of range: {v_total}"
        raise RuntimeError(msg)
    # compute temperature
    temperature = 0
    for n, c in enumerate(d_coef):
        temperature += c * math.pow(v_total, n)
    return temperature


class MAX31855(MAX318xx):
    """
    Class to interface with MAX31855 thermocouple-to-digital converter.

    Args:
        cs_pin (int): Chip select GPIO pin. Default is 24.
        miso_pin (int): MISO GPIO pin. Default is 5.
        clk_pin (int): CLK GPIO pin. Default is 7.
        invert_sign (bool): Whether to invert the sign of the temperature reading (default: False).

    Methods:
        read_temperature(): Returns the temperature in Celsius.
    """

    def __init__(self, cs_pins: dict, miso_pin: int = 5, clk_pin: int = 7, invert_sign: bool = False) -> None:
        """
        Initialize the MAX31855 sensor.

        Args:
            cs_pin: List of chip select GPIO pin numbers.
            miso_pin (int): MISO GPIO pin number.
            clk_pin (int): Clock GPIO pin number.
            invert_sign (bool): Optional, invert temperature sign.
        """
        super().__init__(cs_pins=cs_pins, miso_pin=miso_pin, mosi_pin=None, clk_pin=clk_pin)
        self.invert_sign = invert_sign

    @staticmethod
    def convert_bits(data: list) -> tuple[int, int]:
        """Convert raw bits from sensor to temperature readings.

        Args:
            data (list): List of integers representing raw bits.

        Returns:
            tuple: (t_tc, t_ref) where:
                t_tc (float): Thermocouple temperature.
                t_ref (float): Cold junction (reference) temperature.
        """
        t_tc = 0
        for i in range(-2, 10):
            t_tc += data[18:30][i + 2] * 2**i
        t_ref = 0
        for i in range(-4, 6):
            t_ref += data[4:14][i + 4] * 2**i
        return t_tc, t_ref  # TODO: why is the temperature an int? Is this no real temperature?

    def transform_bytes(self, data: list) -> tuple[int, int]:
        """
        Extract temperature data from raw byte list.

        Args:
            data (list): List of bytes received from sensor.

        Returns:
            tuple: (t_tc, t_ref)
                t_tc (float): Thermocouple temperature.
                t_ref (float): Cold junction (reference) temperature.
        """
        byte_list = []
        for integer in data:
            byte_list = [
                integer >> i & 1 for i in range(8)
            ] + byte_list  # flips bits per byte therefore bytes are also flipped!
        if byte_list[0]:
            raise RuntimeError("Open Circuit on CS" + str(self.cs_pins))
        if byte_list[1]:
            raise RuntimeError("Short to GND on CS" + str(self.cs_pins))
        if byte_list[2]:
            raise RuntimeError("Short to Vcc on CS" + str(self.cs_pins))
        if byte_list[16]:
            raise RuntimeError("Fault on CS" + str(self.cs_pins))
        if byte_list[15]:
            self.invert_sign = not self.invert_sign
        t_tc, t_ref = self.convert_bits(byte_list)
        return t_tc, t_ref  # TODO: why is the temperature an int? Is this no real temperature?

    def read_temp(self, cs_pin: int, num_registers: int, convert: Callable[[float, float], float]) -> float:
        """Read temperature on port `cs_pin`."""  # TODO: better docstring
        data = self.read_register(cs_pin, num_registers)
        t_remote, t_ambient = self.transform_bytes(data)
        t_cal = convert(t_remote, t_ambient)
        if self.invert_sign:
            return -t_cal
        return t_cal

    def _observable_data(self, convert: Callable[[float, float], float] = temperature_NIST) -> dict:
        """Read thermocouple and reference junction temperature, then convert with method from datasheet.

        https://datasheets.maximintegrated.com/en/ds/MAX31855.pdf

        Args:
            convert (function): Function to convert raw temperatures into desired units (default: temperature_NIST).

        Returns:
            dict: Dictionary with key 'temperature' pointing to a tuple of (value, unit).
        """
        log.spam(f"using conversion function: {convert!r}")
        values = [self.read_temp(cs_pin, 4, convert) for key, cs_pin in self.cs_pins.items()]
        return self.create_dict(values, "temperature", "degC")
