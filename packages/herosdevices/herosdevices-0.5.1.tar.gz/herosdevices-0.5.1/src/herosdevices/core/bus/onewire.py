"""This module provides a class for managing OneWire connections."""

from collections.abc import Callable
from pathlib import Path

from herosdevices.helper import log


class OneWire:
    """A read-only Onewire driver that relies on the Linux kernel w1 driver.

    Linux exposes onewire devices in sysfs.
    This driver can read the sysfs files as they are specified in the :param sensors: list.
    """

    # the _obervables describe which quantities can be extracted from the onewire device. The list entries have the
    # form (name_of_observable, conversion_function, unit). The "name_of_observable" must be an endpoint in the sysfs
    # directory of the onewire device.
    _observables: list[tuple[str, Callable, str]] = []

    def __init__(self, device_id: str, sysfs_path: str = "/sys/bus/w1/") -> None:
        """
        Initialize a onewire connection to a device.

        Args:
            device_id: id of the onewire device as named by the w1 Linux kernel driver.
            sysfs_path: sys path of the Linux w1 kernel driver
        """
        self.sysfs_path = Path(sysfs_path) / "devices" / device_id
        if not Path(self.sysfs_path).exists():
            log.error(f"Can not access Linux w1 sysfs path {sysfs_path}")

    def _observable_data(self) -> dict[str, tuple[float, str]]:
        try:
            return {
                observable: (conversion(self._read_content(self.sysfs_path / observable)), unit)
                for observable, conversion, unit in self._observables
            }
        except ValueError:
            return {}

    def _read_content(self, path: Path) -> str | None:
        """Read Contents of :param path: (str) filename."""
        try:
            with path.open("r") as file:
                return "".join(file.readlines())
        except (OSError, TypeError, ValueError):
            log.warning(f"Could not read file {path}")
            return None
