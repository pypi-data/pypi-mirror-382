"""Templates for devices connect via a serial interface."""

from herosdevices.core.bus.serial import SerialConnection


class SerialDeviceTemplate:
    """Template (base class) for devices which are controlled or read out through a serial interface.

    The interface must be accessible via pyserial. This can be via UART, Serial via IP, etc.

    Inheriting your device driver from this class allows to use `herosdevices.core.DeviceCommandQuantity` to define
    the serial commands within your device driver class.
    """

    def __init__(
        self,
        address: str,
        baudrate: int,
        line_termination: bytes = b"\n",
        keep_alive: bool = True,
        delays: dict | None = None,
        **kwargs,
    ) -> None:
        self.address = address
        self.connection = SerialConnection(address, baudrate, line_termination, keep_alive, delays, **kwargs)
