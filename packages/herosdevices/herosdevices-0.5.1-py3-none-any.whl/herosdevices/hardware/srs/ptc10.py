"""HERO Drivers for the SRS PTC10 programmable temperature controller."""

from typing import Any, Literal, overload

from herosdevices.core import DeviceCommandQuantity
from herosdevices.core.templates import TelnetDeviceTemplate
from herosdevices.helper import add_class_descriptor


class PTC10(TelnetDeviceTemplate):
    r"""Driver for the SRS PTC10 programmable temperature controller.

    This driver connects via telnet to the ethernet port.

    Args:
        address: IP address of the device.
        channels_out: Names of the output channels.
        channels_tc: Names of PTC330 extension cards input channels.
        macros: A dict of macros which are written to the temperature controller and can be called with
            :py:meth:`run_macro`. The dictionary keys are the names and the values the actual macro code. Note, that
            the macro content must be a single line string.
        observables: A dictionary of attributes that are emitted with the `observable_data` event if the device is
            started as a `PolledDatasourceHero`. If no values are given, the set temperature, actual temperature and
            TEC power are emitted.

    Besides the implemented functions, you can also directly send raw commands to the controller by using
    :py:meth:`send_raw_command` for maximum flexibility.

    Example:
        The class can be started with BOSS with the following example JSON dict::

            {
              "_id": "oven-controller",
              "classname": "herosdevices.hardware.srs.PTC10",
              "active": true,
              "arguments": {
                "address": "192.168.50.15",
                "channels_tc": [
                  "WindowTC",
                  "OvenTC"
                ],
                "channels_out": [
                  "WindowOut",
                  "OvenOut"
                ],
                "macros": {
                  "OvenOn": "if (OvenOut.PID.setpoint==0) OvenOut.PID.setpoint=50 }else{ popup \"Oven already on\" }"
                }
              },
              "datasource": {
                "async": false,
                "interval": 300
              }
            }
    """

    observables: dict
    macros: dict | None=None

    def __new__(cls, channels_tc: list | None = None, channels_out: list | None = None, *_args, **_kwargs) -> "PTC10":
        """Create a new PTC10 instance.

        Sets up the object to use the specified channel names for the output and input channels of the device and
        expose them to HEROS as they can be only addressed by the name which is user-defined.

        Args:
            channels_tc: List of temperature channel names.
            channels_out: List of output channel names.
        """
        cls.default_observables = {}
        for channel in channels_tc or []:
            name_str = f"{channel}_temp_act"
            add_class_descriptor(
                cls, name_str, DeviceCommandQuantity(command_get=f"{channel}.value?\n", dtype=float, unit="°C")
            )
            cls.default_observables[name_str] = {"name": name_str, "unit": "°C"}
        for channel in channels_out or []:
            name_str_t = f"{channel}_temp"
            name_str_p = f"{channel}_power_act"
            add_class_descriptor(
                cls,
                name_str_t,
                DeviceCommandQuantity(
                    command_get=f"{channel}.PID.setpoint?\n",
                    command_set=f"{channel}.PID.setpoint={{}}\n",
                    dtype=float,
                    unit="°C",
                ),
            )
            add_class_descriptor(
                cls, name_str_p, DeviceCommandQuantity(command_get=f"{channel}.value?\n", dtype=float, unit="W")
            )
            cls.default_observables[name_str_t] = {"name": name_str_t, "unit": "°C"}
            cls.default_observables[name_str_p] = {"name": name_str_p, "unit": "W"}
        return super().__new__(cls)

    def __init__(
        self, address: str, *_args, macros: dict | None = None, observables: dict | None = None, **_kwargs
    ) -> None:
        super().__init__(address, 23)

        self.observables = observables if observables is not None else self.default_observables
        self.macros = macros if macros is not None else {}

    @overload
    def send_raw_command(self, command: str, read_echo: Literal[False] = False) -> None: ...
    @overload
    def send_raw_command(self, command: str, read_echo: Literal[True]) -> str: ...

    def send_raw_command(self, command: str, read_echo: bool = False) -> None | str:
        r"""Send a command to the device.

        Args:
            command: Command to send. Can end (but does not have to) in a command termination like `\n`. See the device
                manual for available commands.
            read_echo: If a response should be read from the device.
        """
        if not command.endswith(("\n", "\r")):
            command += "\n"
        return self.connection.write(command, read_echo=read_echo)

    def stop_macro(self, name: str) -> None | str:
        """
        Stop a running macro.

        Args:
            name: Name of the macro to stop.
        """
        return self.connection.write(f"kill {name}\n", read_echo=True, read_line=False)

    def run_macro(self, name: str) -> str:
        """Run a macro on the hardware.

        If the macro is present in the macros dictionary (see :py:meth:`__init__` for details), it will be send to
        the device first.

        Args:
            name: Name of the macro to run.
        """
        if name in self.macros:
            self.define_macro(name, self.macros[name])
        return self.connection.write(f"run {name}\n", read_echo=True, read_line=False)

    def define_macro(self, name: str, content: str) -> str:
        """
        Send a new macro with the given name and content to the device.

        Args:
            name: Name of the macro to define.
            content: The content of the macro.
        """
        macro_string = f"define {name} ( {content} )\n"
        self.macros[name] = content
        return self.connection.write(macro_string, read_echo=True, read_line=False)

    def _observable_data(self) -> dict[str, tuple[Any, str]]:
        data = {}
        for attr, description in self.observables.items():
            data[description["name"]] = (getattr(self, attr), description["unit"])
        return data
