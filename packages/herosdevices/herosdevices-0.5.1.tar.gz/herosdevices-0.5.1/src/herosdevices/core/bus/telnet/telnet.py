"""This module provides a class for managing telnet connections and a context manager for handling telnet sessions."""

import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Literal, overload

from heros.helper import log

from .telnetlib import IAC, NOP, Telnet

TELNET_DELAYS_DEFAULT: dict = {"write": 0.001, "read_echo": 0.001}


class TelnetConnection:
    """A class to manage telnet communication connections.

    This class provides functionality to handle telnet connections including opening/closing connections, reading
    data, and writing data.

    Args:
        address: The address of the telnet socket, something like /dev/ttyUSB0.
        port: Port the telnet server is listening on
        line_termination: character that terminates a line in the communication.
        keep_alive: Flag indicating whether to keep the connection open between operations.
        delays: Dictionary containing delay times for in between telnet operations.
            Default telnet delays for telnet devices. Available keys are:

                * "write": Time to wait after writing a command to the device.
                * "read_echo": Time to wait before reading a response from the device.

            :py:data:`herosdevices.core.bus.telnet.TELNET_DELAYS_DEFAULT` sets the default delays.
    """

    def __init__(
        self,
        address: str,
        port: int = 23,
        timeout: float = 1.0,
        line_termination: bytes = b"\n",
        keep_alive: bool = True,
        delays: dict | None = None,
    ) -> None:
        self.address = address
        self.port = port
        self.timeout = timeout
        self.line_termination = line_termination
        self.connection = Telnet()
        self.keep_alive = keep_alive
        self.delays = TELNET_DELAYS_DEFAULT | delays if delays else TELNET_DELAYS_DEFAULT

    def check_alive(self) -> bool:
        """Check if the telnet connection is alive."""
        try:
            if self.connection.sock:  # this way I've taken care of problem if the .close() was called
                self.connection.sock.send(IAC + NOP)  # notice the use of send instead of sendall
                return True
        except OSError:
            pass
        return False

    @contextmanager
    def operation(self) -> Iterator[None]:
        """Context manager for handling telnet connection operations.

        Ensures the telnet connection is open before performing operations and closes it afterward
        if :code:`self.keep_alive` is False.

        Yields:
            Yields control back to the caller for performing operations within the context.
        """
        if not self.check_alive():
            self.connection.open(self.address, self.port, self.timeout)
        try:
            yield
        finally:
            if not self.keep_alive:
                self.connection.close()

    def wait(self, operation: str) -> None:
        """Introduce a (synchronous) delay based on the specified operation type.

        Args:
            operation: The operation type. For possible types see :code:`TELNET_DELAYS_DEFAULT`.
        """
        time.sleep(self.delays[operation])

    def read(self) -> str | None:
        """
        Read all available data from the telnet connection and decodes it into a string.

        Returns:
            The decoded data as string, or None if an error occurs.
        """
        with self.operation():
            try:
                read = self.connection.read_very_eager()
                return read.decode("ascii")
            except Exception as e:  # noqa: BLE001
                log.error(
                    "Error reading from telnet connection at %s: %s",
                    self.address,
                    e,
                )
                return None

    def read_line(self) -> str | None:
        """Read a single line from the telnet connection.

        Returns:
            The decoded line as string, or None if an error occurs.
        """
        with self.operation():
            try:
                read = self.connection.read_until(self.line_termination)
                return read.decode("ascii")
            except Exception as e:  # noqa: BLE001
                log.error(
                    "Error reading from telnet connection at %s: %s",
                    self.address,
                    e,
                )
                return None

    @overload
    def write(self, message: str, read_echo: Literal[True] = True, read_line: bool = True) -> str: ...
    @overload
    def write(self, message: str, read_echo: Literal[False], read_line: bool = True) -> None: ...
    @overload
    def write(self, message: str, read_echo: bool = False, read_line: bool = True) -> str | None: ...

    def write(self, message: str, read_echo: bool = False, read_line: bool = True) -> str | None:
        """Write a message to the telnet connection.

        Args:
            message: The message to be written to the telnet connection.
            read_echo: If True, reads back the echo after writing. Defaults to False.
            read_line: If True, data is read until `self.line_termination` occurs in the data. Otherwise all available
                data is read.

        Returns:
            If read_echo is True, returns the echo read from the connection as string; otherwise returns None.
        """
        with self.operation():
            self.connection.read_very_lazy()
            self.connection.write(message.encode("ascii"))
            self.wait("write")
            if read_echo:
                if read_line:
                    read = self.read_line()
                else:
                    self.wait("read_echo")
                    read = self.read()
                return read
            return None
