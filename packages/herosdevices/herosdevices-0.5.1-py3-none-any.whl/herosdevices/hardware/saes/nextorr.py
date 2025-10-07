"""Device driver for SAES NEXTorr non-evaporative getter/sputter ion pump controller NIOPS."""

from herosdevices.core import DeviceCommandQuantity
from herosdevices.core.templates import SerialDeviceTemplate as SerialDevice
from herosdevices.helper import log


def _niops_current_format(hex_value: str) -> float:
    """Convert a hexadecimal value to a current measurement in amperes (A), microamperes (µA), or nanoamperes (nA).

    The function interprets the hexadecimal input as a 16-bit value, where the two most significant bits (bits 14-15)
    determine the multiplier (range) for the current measurement. The remaining 14 bits represent the raw value.

    Args:
        hex_value (str): A hexadecimal string representing the current measurement.
    """
    multiplier = [1e-9, 1e-7, 1e-5]
    value = int(hex_value, 16)
    rr = (value & 0b11 << 14) >> 14
    return (value & (2**14 - 1)) * multiplier[rr]


class NEXTorr(SerialDevice):
    """A NEXTorr vacuum pump with serial based connection."""

    pressure = DeviceCommandQuantity(command_get="Tb\r", dtype=float)  # pressure in mbar
    voltage = DeviceCommandQuantity(command_get="u\r", dtype=float, format_fun=lambda x: int(x, 16))  # voltage in volt
    current = DeviceCommandQuantity(command_get="i\r", dtype=float, format_fun=_niops_current_format)  # current in amp
    version = DeviceCommandQuantity(command_get="V\r", dtype=str)

    def __init__(self, device: str, baudrate: int = 115200) -> None:
        """
        Initialize the NEXTorr device driver.

        Args:
            device: Serial device address. Typically /dev/ttyUSB0 or similar.
        """
        SerialDevice.__init__(self, device, baudrate=baudrate, line_termination=b"\r", keep_alive=False)

    def ion_pump_on(self) -> bool:
        """Turn the integrated sputter ion pump on."""
        return self.write("G\r", read_echo=True) == "$\r"

    def ion_pump_off(self) -> bool:
        """Turn the integrated sputter ion pump off."""
        return self.write("B\r", read_echo=True) == "$\r"

    def ion_pump_set_voltage(self, voltage: int) -> bool:
        """Set the integrated sputter ion pump voltage.

        Args:
            voltage: Voltage in V
        """
        return self.write(f"U{int(voltage):04x}" + "\r", read_echo=True) == "$\r"

    def _observable_data(self) -> dict | None:
        try:
            return {"pressure": (self.pressure, "mbar"), "voltage": (self.voltage, "V"), "current": (self.current, "A")}
        except Exception:  # noqa: BLE001
            log.exception("Error reading observable data")
