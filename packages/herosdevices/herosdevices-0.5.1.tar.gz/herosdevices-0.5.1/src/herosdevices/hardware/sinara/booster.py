"""Hardware driver for the Booster RF amplifiers."""

from datetime import datetime
from types import TracebackType
from typing import NamedTuple

import dateutil.parser
import serial

from herosdevices.helper import log


class Version(NamedTuple):
    """A named tuple representing the version information of a device."""

    fw_rev: str
    fw_hash: str
    fw_build_date: datetime
    device_id: str
    hw_rev: str


class Status_short(NamedTuple):
    """A named tuple representing the short version status information of a device."""

    detected: bool
    enabled: bool
    interlock: bool
    output_power_mu: int
    reflected_power_mu: int
    I29V: float
    I6V: float
    V5VMP: float
    temp: float
    output_power: float
    reflected_power: float


class Status_long(NamedTuple):
    """A named tuple representing the long version status information of a device."""

    detected: bool
    enabled: bool
    interlock: bool
    output_power_mu: int
    reflected_power_mu: int
    I29V: float
    I6V: float
    V5VMP: float
    temp: float
    output_power: float
    reflected_power: float
    input_power: float
    fan_speed: float
    error_occurred: bool
    hw_id: str
    i2c_error_count: int


# Unit mapping
UNIT_MAP = {
    "detected": "",
    "enabled": "",
    "interlock": "",
    "output_power_mu": "",
    "reflected_power_mu": "",
    "output_power": "dBm",
    "reflected_power": "dBm",
    "input_power": "dBm",
    "I29V": "A",
    "I6V": "A",
    "V5VMP": "V",
    "temp": "degC",
    "fan_speed": "percent",
    "error_occurred": "",
    "hw_id": "",
    "i2c_error_count": "",
}


class Booster:
    """Booster 8-channel RF Amplifier."""

    def __init__(self, device: str, port: int = 5000, read_timeout: float = 1, *_args, **_kwargs) -> None:
        # TODO: why to we keep args/kwargs here?
        self.dev = serial.serial_for_url(f"socket://{device}:{port}", timeout=read_timeout)
        self.dev.reset_input_buffer()
        assert self.ping()

    def __enter__(self) -> "Booster":
        """Contextmanager method to open/close the device."""
        return self

    def __exit__(
        self, _exc_type: type[BaseException] | None, _exc_val: BaseException | None, _exc_tb: TracebackType | None
    ) -> None:
        """Run :py:meth:`Booster.teardown` on exit."""
        self.teardown()

    def _cmd(self, cmd: str, channel: int | None, arg: str | float | None = None) -> str | bool:
        if channel is not None and channel not in range(8):
            msg = f"invalid channel number {channel}"
            raise ValueError(msg)

        if channel is None and arg is None:
            cmd = cmd + "\n"
        elif arg is None:
            cmd = f"{cmd} {channel}\n"
        else:
            cmd = f"{cmd} {channel}, {arg}\n"
        self.dev.write(cmd.encode())

        # see https://github.com/sinara-hw/Booster/issues/347
        response = self.dev.readline().decode()
        if response == "":
            self.dev.write(b"\n")
            response = self.dev.readline().decode()
            self.dev.readline()  # blank response from extra write
            if response == "":
                msg = f"Timeout while waiting for response to '{cmd.strip()}'"
                raise serial.SerialTimeoutException(msg)
        response = response.lower().strip()

        if "?" in cmd and "error" not in response:
            return response
        if response == "ok":
            return True

        msg = f"Unrecognised response to '{cmd}': '{response}'"
        raise RuntimeError(msg)

    def _query_bool(self, cmd: str, channel: int, arg: str | float | None = None) -> bool:
        resp = self._cmd(cmd, channel, arg)
        if resp == "0":
            return False
        if resp == "1":
            return True
        msg = f"Unrecognised response to {cmd}: '{resp}'"
        raise RuntimeError(msg)

    def _query_float(self, cmd: str, channel: int | None, arg: str | float | None = None) -> float:
        resp = self._cmd(cmd, channel, arg)
        try:
            return float(resp)
        except ValueError as e:
            msg = f"Unrecognised response to {cmd}: '{resp}'"
            raise RuntimeError(msg) from e

    def get_version(self) -> Version:
        """Return the device version information as a named tuple."""
        self.dev.write(b"*IDN?\n")
        idn = self.dev.readline().decode().strip().lower().split(",")

        idn[0] = idn[0].split(" ")

        if (
            idn[0][0] != "rfpa"
            or not idn[1].startswith(" built ")
            or not idn[2].startswith(" id ")
            or not idn[3].startswith(" hw rev ")
        ):
            msg = f"Unrecognised device identity string: {idn}"
            raise RuntimeError(msg)

        return Version(
            fw_rev=idn[0][1],
            fw_hash=idn[0][2],
            fw_build_date=dateutil.parser.parse(idn[1][7:]),
            device_id=idn[2][4:],
            hw_rev=idn[3][1:],
        )

    def ping(self) -> bool:
        """Return True if we are connected to a Booster."""
        try:
            self.get_version()
        except Exception:  # noqa: BLE001
            return False
        return True

    def set_enabled(self, channel: int, enabled: bool = True) -> None:
        """Enable/disable a channel."""
        cmd = "CHAN:ENAB" if enabled else "CHAN:DISAB"
        self._cmd(cmd, channel)

    def get_enabled(self, channel: int) -> bool:
        """Return True is the channel is enabled."""
        return self._query_bool("CHAN:ENAB?", channel)

    def get_detected(self, channel: int) -> bool:
        """Return True is the channel is detected, otherwise False.

        Non-detected channels indicate a serious hardware error!
        """
        return self._query_bool("CHAN:DET?", channel)

    def get_status(self, channel: int) -> Status_short | Status_long:
        """
        Return a named tuple containing information about the status of a given channel.

        .. list-table:: Channel Status Fields
            :header-rows: 1
            :widths: 20 80

            * - Field
              - Description
            * - detected
              - True if the channel is detected
            * - enabled
              - True if the channel was enabled
            * - interlock
              - True if the interlock has tripped for this channel
            * - output_power_mu
              - Output (forward) power detector raw ADC value
            * - reflected_power_mu
              - Output reverse power detector raw ADC value
            * - output_power
              - Output (forward) power (dBm)
            * - reflected_power
              - Output reverse power (dBm)
            * - input_power
              - Input power (dBm)
            * - I29V
              - Current consumption on the main 29V rail (A)
            * - I6V
              - Current consumption on the 6V (preamp) rail (A)
            * - V5VMP
              - Voltage on the 5VMP rail
            * - temp
              - Channel temperature (°C)
            * - fan_speed
              - Chassis fan speed (%)
            * - error_occurred
              - True if an error (e.g. over temperature) has occurred, otherwise False.
                Error conditions can only be cleared by power-cycling Booster.
            * - hw_id
              - Unique ID number for the channel
            * - i2c_error_count
              - Number of I2C bus errors that have been detected for this channel
        """
        raw_resp = self._cmd("CHAN:DIAG?", channel)
        if type(raw_resp) is str:
            resp = raw_resp.split(",")
        else:
            raise RuntimeError("Unrecognised response to 'CHAN:DIAG?'")

        def _bool(value_str: str) -> bool:
            if value_str == "1":
                return True
            if value_str == "0":
                return False
            raise RuntimeError("Unrecognised response to 'CHAN:DIAG?'")

        if len(resp) == 12:  # noqa: PLR2004
            return Status_short(
                detected=_bool(resp[0]),
                enabled=_bool(resp[1]),
                interlock=_bool(resp[2]),
                output_power_mu=int(resp[4]),
                reflected_power_mu=int(resp[5]),
                I29V=float(resp[6]),
                I6V=float(resp[7]),
                V5VMP=float(resp[8]),
                temp=float(resp[9]),
                output_power=float(resp[10]),
                reflected_power=float(resp[11]),
            )

        if len(resp) == 22:  # noqa: PLR2004
            return Status_long(
                detected=_bool(resp[0]),
                enabled=_bool(resp[1]),
                interlock=_bool(resp[2]),
                output_power_mu=int(resp[4]),
                reflected_power_mu=int(resp[5]),
                I29V=float(resp[6]),
                I6V=float(resp[7]),
                V5VMP=float(resp[8]),
                temp=float(resp[9]),
                output_power=float(resp[10]),
                reflected_power=float(resp[11]),
                input_power=float(resp[12]),
                fan_speed=float(resp[13]),
                error_occurred=_bool(resp[14]),
                hw_id="{:x}:{:x}:{:x}:{:x}:{:x}:{:x}".format(*[int(part) for part in resp[15:21]]),
                i2c_error_count=int(resp[21]),
            )

        raise RuntimeError("Unrecognised response to 'CHAN:DIAG?'")

    def get_current(self, channel: int) -> float:
        """Return the FET bias current (A) for a given channel."""
        return self._query_float("MEAS:CURR?", channel)

    def get_temperature(self, channel: int) -> float:
        """Return the temperature (C) for a given channel."""
        return self._query_float("MEAS:TEMP?", channel)

    def get_output_power(self, channel: int) -> float:
        """Return the output (forwards) power for a channel in dBm."""
        return self._query_float("MEAS:OUT?", channel)

    def get_input_power(self, channel: int) -> float:
        """Return the input power for a channel in dBm."""
        return self._query_float("MEAS:IN?", channel)

    def get_reflected_power(self, channel: int) -> float:
        """Return the reflected power for a channel in dBm."""
        return self._query_float("MEAS:REV?", channel)

    def get_fan_speed(self) -> float:
        """Return the fan speed as a number between 0 and 100."""
        return self._query_float("MEAS:FAN?", None)

    def set_interlock(self, channel: int, threshold: float) -> str | bool:
        """Set the output forward power interlock threshold (dBm) for a given channel channel.

        This setting is stored in non-volatile memory and retained across power
        cycles.

        :param threshold: must lie between 0dBm and 38dBm
        """
        if (threshold < 0) or (threshold > 38):  # noqa: PLR2004
            raise ValueError("Output forward power interlock threshold must lie between 0dBm and +38dBm")
        return self._cmd("INT:POW", channel, f"{threshold:.0f}")

    def get_interlock(self, channel: int) -> float:
        """Return the output forward power interlock threshold (dBm) for a channel."""
        return self._query_float("INT:POW?", channel)

    def clear_interlock(self, channel: int) -> None:
        """Reset the forward and reverse power interlocks for a given channel."""
        self._cmd("INT:CLEAR", channel)

    def get_interlock_tripped(self, channel: int) -> bool:
        """Return True if the output forwards or reverse power interlock has tripped for a given channel."""
        return self._query_bool("INT:STAT?", channel)

    def get_forward_power_interlock_tripped(self, channel: int) -> bool:
        """Return True if the output forwards power interlock has tripped for a given channel."""
        return self._query_bool("INT:FOR?", channel)

    def get_reverse_power_interlock_tripped(self, channel: int) -> bool:
        """Return True if the output forwards power interlock has tripped for a given channel."""
        return self._query_bool("INT:REV?", channel)

    def get_error_occurred(self, channel: int) -> bool:
        """Return True if a device error (over temperature etc) has occurred on a given channel."""
        return self._query_bool("INT:ERR?", channel)

    def _observable_data(self) -> dict:
        """Return dict of field name to (value, unit) for a given status namedtuple."""
        status_dict = {}
        for chan in range(8):
            status = self.get_status(chan)
            inner_dict = {
                f"ch{chan:.0f}_{field}": (getattr(status, field), UNIT_MAP.get(field, "")) for field in status._fields
            }
            status_dict.update(inner_dict)
        log.debug("Emitting observable_data")
        return status_dict

    def teardown(self) -> None:
        """Close the device connection."""
        self.dev.close()
