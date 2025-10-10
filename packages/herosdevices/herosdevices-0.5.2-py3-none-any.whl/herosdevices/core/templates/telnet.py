"""Templates for devices connected via a legacy telnet interface."""

from herosdevices.core.bus.telnet import TelnetConnection


class TelnetDeviceTemplate:
    """Device representation template for devices connected via a telnet connection.

    To make a functional device, the user needs to implement the actual device representation in an abstracted class.
    This template handles the connection object and exposes the connection via `self.connection` and the methods
    `self.read` and `self.write` which are aliases to the underlying
    py:meth:`herosdevices.core.bus.telnet.TelnetConnection.read` and
    py:meth:`herosdevices.core.bus.telnet.TelnetConnection.write`.

    The template allows the usage of :py:class:`herosdevices.core.DeviceCommandQuantity`.
    """

    def __init__(self, address: str, port: int = 23, timeout: float = 1.0, **kwargs) -> None:
        self.address = address
        self.connection = TelnetConnection(address, port=port, timeout=timeout, **kwargs)
        self.write = self.connection.write
        self.read = self.connection.read
