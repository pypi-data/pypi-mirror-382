"""Includes classes for controlling Gamma Vacuum Ltd devices."""

from herosdevices.core import DeviceCommandQuantity
from herosdevices.core.templates import SerialDeviceTemplate, TelnetDeviceTemplate
from herosdevices.helper import extract_regex

DEFAULT_OBSERVABLES = {"pressure": {"name": "pressure", "unit": "mBar"}}


class EthernetSPC(TelnetDeviceTemplate):
    """Controller for the Gamma vacuum SPC Ion pump controllers with **network** interface."""

    pressure = DeviceCommandQuantity(
        command_get="spc 0B \r\n",
        dtype=float,
        unit="mBar/Torr/Pa",
        format_fun=extract_regex(r"[+-]?\d+\.\d+[Ee][+-]?\d+"),
    )

    current = DeviceCommandQuantity(
        command_get="spc 0A \r\n",
        dtype=float,
        unit="A",
        format_fun=extract_regex(r"[+-]?\d+\.\d+[Ee][+-]?\d+"),
    )

    voltage = DeviceCommandQuantity(
        command_get="spc 0C \r\n",
        dtype=float,
        format_fun=extract_regex(r"(\d+)[\r]+"),
        unit="V",
    )

    hv_on = DeviceCommandQuantity(
        command_get="spc 61 \r\n",
        dtype=bool,
        format_fun=lambda x: "YES" in x,
    )

    observables: dict

    def __init__(self, address: str, observables: dict | None = None, *args, **kwargs) -> None:
        """Initialize device driver object.

        Args:
            address: IP address of the target device.
            observables: Dictionary of attributes which should be exposed at datasource :py:meth:`_observable_data`
                events. Of the form {"attribute_name": {"name": "display_name", "unit": "unit"}}.

        ``args`` and ``kwargs`` are passed to the :py:class:`herosdevices.core.templates.TelnetDeviceTemplate`
        constructor.
        """
        super().__init__(address, 23, *args, line_termination=b"\r", **kwargs)
        self.observables = observables if observables is not None else DEFAULT_OBSERVABLES

    def _observable_data(self) -> dict:
        data = {}
        for attr, description in self.observables.items():
            data[description["name"]] = (getattr(self, attr), description["unit"])
        return data


class SerialSPC(SerialDeviceTemplate):
    """Controller for the Gamma vacuum SPC Ion pump controllers with a **serial** interface."""

    pressure = DeviceCommandQuantity(
        command_get="~ 01 0B 00\r",
        dtype=float,
        unit="mBar/Torr/Pa",
        format_fun=extract_regex(r"[+-]?\d+\.\d+[Ee][+-]?\d+"),
    )

    current = DeviceCommandQuantity(
        command_get="~ 01 0A 00\r",
        dtype=float,
        unit="A",
        format_fun=extract_regex(r"[+-]?\d+\.\d+[Ee][+-]?\d+"),
    )

    voltage = DeviceCommandQuantity(
        command_get="~ 01 0C 00\r",
        dtype=float,
        format_fun=extract_regex(r"(\d+)[\r]+"),
        unit="V",
    )

    hv_on = DeviceCommandQuantity(
        command_get="~ 01 61 00\r",
        dtype=bool,
        format_fun=lambda x: "YES" in x,
    )

    def __init__(self, address: str, observables: dict | None = None, *args, **kwargs) -> None:
        """Initialize device driver object.

        Args:
            address: Serial port address of the target device.
            observables: Dictionary of attributes which should be exposed at datasource :py:meth:`_observable_data`
                events. Of the form {"attribute_name": {"name": "display_name", "unit": "unit"}}.

        ``args`` and ``kwargs`` are passed to the :py:class:`herosdevices.core.templates.SerialDeviceTemplate
        constructor.
        """
        super().__init__(address, *args, baudrate=19200, line_termination=b"\r", **kwargs)
        self.observables = observables if observables is not None else DEFAULT_OBSERVABLES

    def _observable_data(self) -> dict:
        data = {}
        for attr, description in self.observables.items():
            data[description["name"]] = (getattr(self, attr), description["unit"])
        return data
