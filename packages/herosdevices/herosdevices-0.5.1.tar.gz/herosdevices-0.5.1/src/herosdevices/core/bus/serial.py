"""Primitive functions and classes representing serial connections."""

import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from types import ModuleType

from heros.helper import log

SERIAL_DELAYS_DEFAULT: dict = {"write": 0.001, "read_echo": 0.001, "flush": 0.001}


try:
    import serial
except ModuleNotFoundError:
    serial = cast("ModuleType", None)


class SerialConnection:
    """A class to manage serial communication connections.

    This class provides functionality to handle serial connections including opening/closing connections, reading
    data, and writing data. It inherits from the base class Connection.

    Args:
        address: The address of the serial socket, something like /dev/ttyUSB0.
        baudrate: The baud rate for the serial communication.
        line_termination: character that terminates a line in the communication.
        keep_alive: Flag indicating whether to keep the connection open between operations.
        delays: Dictionary containing delay times for in between serial operations.
            Default serial delays for serial devices. Available keys are:

                * "write": Time to wait after writing a command to the device.
                * "read_echo": Time to wait before reading a response from the device.
                * "flush": Time to wait after flushing the device.

            :py:data:`herosdevices.core.bus.SERIAL_DELAYS_DEFAULT` sets the default delays.
        **kwargs: Keyword arguments passed to :code:`serial.serial_for_url`
    """

    def __init__(
        self,
        address: str,
        baudrate: int = 115200,
        line_termination: bytes = b"\n",
        keep_alive: bool = True,
        delays: dict | None = None,
        **kwargs,
    ) -> None:
        self.address = address
        self.baudrate = baudrate
        self.line_termination = line_termination
        if serial is None:
            raise ModuleNotFoundError(
                "Could not import the 'pyserial' python module, serial devices are not be available"
            )
        self.connection = serial.serial_for_url(address, do_not_open=True, baudrate=baudrate, **kwargs)
        self.keep_alive = keep_alive
        self.delays = SERIAL_DELAYS_DEFAULT | delays if delays else SERIAL_DELAYS_DEFAULT

    @contextmanager
    def operation(self) -> Iterator[None]:
        """Context manager for handling serial connection operations.

        Ensures the serial connection is open before performing operations and closes it afterward
        if :code:`self.keep_alive` is False.

        Yields:
            Yields control back to the caller for performing operations within the context.
        """
        if not self.connection.isOpen():
            self.connection.open()
        try:
            yield
        finally:
            if not self.keep_alive:
                self.connection.close()

    def wait(self, operation: str) -> None:
        """Introduce a (synchronous) delay based on the specified operation type.

        Args:
            operation: The operation type. For possible types see :code:`SERIAL_DELAYS_DEFAULT`.

        """
        time.sleep(self.delays[operation])

    def read(self) -> str | None:
        """Read all available data from the serial connection and decodes it into a string.

        Returns:
            The decoded data as string, or None if an error occurs.
        """
        with self.operation():
            try:
                read = b""
                while bytes_to_read := self.connection.in_waiting > 0:
                    read += self.connection.read(bytes_to_read)
                return read.decode("ascii")
            except Exception:  # noqa: BLE001
                log.exception(
                    "Error reading from serial connection at %s",
                    self.address,
                )
                return None

    def read_line(self) -> str | None:
        """Read a single line from the serial connection.

        Returns:
            The decoded line as string, or None if an error occurs.
        """
        with self.operation():
            try:
                read = self.connection.read_until(self.line_termination)
                return read.decode("ascii")
            except Exception:  # noqa: BLE001
                log.exception(
                    "Error reading from serial connection at %s",
                    self.address,
                )
                return None

    def write(self, message: str, flush: bool = True, read_echo: bool = False, read_line: bool = False) -> None | str:
        """Write a message to the serial connection.

        Args:
            message: The message to be written to the serial connection.
            flush: If True, flushes the written data immediately. Defaults to True.
            read_echo: If True, reads back the echo after writing. Defaults to False.
            read_line: If True, data is read until `self.line_termination` occurs in the data. Otherwise all available
                data is read.

        Returns:
            If read_echo is True, returns the echo read from the connection as string; otherwise returns None.
        """
        with self.operation():
            self.connection.reset_input_buffer()
            self.connection.write(message.encode("ascii"))
            self.wait("write")
            if flush:
                self.connection.flush()
                self.wait("flush")
            if read_echo:
                if read_line:
                    read = self.read_line()
                else:
                    self.wait("read_echo")
                    read = self.read()
                return read
        return None
