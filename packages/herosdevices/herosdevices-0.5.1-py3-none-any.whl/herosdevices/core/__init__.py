"""Includes core functionalities relevant to all/many hardware driver implementations."""

import time
from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

from heros.helper import log

FieldType = TypeVar("FieldType")


def any__new__(cls, *_args, **_kwargs) -> Any:  # noqa: ANN001
    """Monkey patch for https://github.com/python/cpython/pull/117111.

    Debian and Ubuntu (and possibly other distros with a slow release cycle) ship a version of python with the
    aforementioned bug.
    """
    if cls is Any:
        raise TypeError("Any cannot be instantiated")
    return object.__new__(cls)


Any.__new__ = any__new__
del any__new__


class DeviceCommandQuantity(Any, Generic[FieldType]):
    """
    Descriptor for attaching getting/setting configuration of hardware directly to class attributes exposed to HEROs.

    This class provides functionality to define a class attribute of the host object based on certain set and get
    commands of a device on a given interface. Defining an attribute this way makes it directly accessible to HEROS.

    args:
        command_set: Command to send to the remote device to set the quantity. Must include a single input
        placeholder in f-string format for the value to be set.
        command_get: Command to send to the remote device to get the quantity.
        return_check: Return value to check for success
        unit: Unit of the quantity.
        dtype: Data type of the quantity values.
        format_fun: Function to format the raw device return value to obtain the quantity in the correct unit.
            For example if the device returns a complicated string, this function could use a regex to extract
            the target value.
        value_check_fun: Function to check if a set value is valid. Can be used in combination with for example
            `:py:func:`herosdevices.core.utils.limits` to check if the value is within a certain range.
        poll_interval_limit: When getting the value of this quantity, the value is only read from the device if the
            last read operation was longer ago than the value of :code:`poll_interval_limit`. If it is shorter, the
            cached value is returned.
        read_line: If true, the value is read from the device as a single line until the line termination set in the
            device connection occurs. If false, all waiting data is read, this is typically slower as one needs a
            longer delay, however it must be used if the return value is multiline.

    Info:
        The host instance must provide :code:`read()->str` and
        :code:`write(message: str, read_echo: bool) -> None | str` methods. For an example implementation see
        :py:class:`herosdevices.core.templates.serial.SerialDeviceTemplate`.

    Warning:
        This mechanism stores values in the device object with the name :code:`instance._{attr_name}` and
        :code:`_{attr_name}_last_poll`, where `attr_name` is the class attribute name (`frequency` in the example
        below). This means you can not implement attributes with these names in you device driver class.


    Example:

        .. code-block:: python

            class SomeRFSource(RFSource):
                frequency = DeviceCommandQuantity(
                    command_set="f{:.3f}",
                    command_get="f?",
                    dtype=float,
                    unit="base",
                    value_check_fun=limits(12.5e6, 5.4e9),
                    transform_fun=transform_unit("base", "MHz"),
                    format_fun=lambda x: float(x)*1e-3,
                )  # Frequency in Hz
    """

    def __init__(
        self,
        command_set: str | None = None,
        command_get: str | None = None,
        return_check: None | str = None,
        unit: str = "",
        dtype: type[FieldType] | None = None,
        format_fun: Callable[[str], Any] = lambda x: x.rstrip(),
        value_check_fun: Callable[[Any], bool | str] = lambda _: True,
        poll_interval_limit: float = 1.0,
        transform_fun: Callable[[Any, bool], Any] = lambda x, _=False: x,
        read_line: bool = True,
    ) -> None:
        self.command_set = command_set
        self.command_get = command_get
        self.return_check = return_check
        self.unit = unit
        self.dtype = dtype
        self.format_fun = format_fun
        self.value_check_fun = value_check_fun
        self.poll_interval_limit = poll_interval_limit
        self.transform_fun = transform_fun
        self.read_line = read_line

    def __set_name__(self, owner, name: str) -> None:  # noqa: ANN001
        """Make the DeviceCommandQuantity instance aware of its parent class."""
        self.name = name
        self.owner = owner

    def __set__(self, instance, value: FieldType) -> None:  # noqa: ANN001
        """Set the value on the physical device. Involves sending and receiving data to/from the device."""
        if (check_return := self.value_check_fun(value)) is not True:
            msg = f"Value {value} {self.unit} is not valid for {self.name}: {check_return}"
            raise ValueError(msg)
        if self.command_set:
            instance.connection.write(self.command_set.format(self.transform_fun(value, False)))
        else:
            log.error(
                "Attribute %s on device %s is not settable",
                self.name,
                self.owner.__name__,
            )
        if self.return_check:
            re = instance.connection.read()
            if re != self.return_check:
                log.error(
                    "Device %s returned error %s when setting %s",
                    self.owner.__name__,
                    re,
                    self.name,
                )
            else:
                setattr(instance, f"_{self.name}_last_poll", time.time())
                setattr(instance, f"_{self.name}", value)

    @overload
    def __get__(self, instance: None, owner: type) -> "DeviceCommandQuantity[FieldType]": ...
    @overload
    def __get__(self, instance: object, owner: type) -> FieldType: ...

    def __get__(self, instance, owner):
        """Read the value from the physical device. Involves sending and receiving data to/from the device.

        Values are cached and fast subsequent reads return the same value without contacting the device.
        """
        if instance is None:
            return self

        # read from device
        if self.command_get:
            if hasattr(instance, f"_{self.name}_last_poll"):
                if time.time() - getattr(instance, f"_{self.name}_last_poll") < self.poll_interval_limit:
                    return getattr(instance, f"_{self.name}")
            restring = instance.connection.write(self.command_get, read_echo=True, read_line=self.read_line)
            if type(restring) is not bool:
                restring = self.format_fun(restring)
                if self.dtype is not None:
                    try:
                        restring = self.dtype(restring)
                    except ValueError as e:
                        log.warning("%s while reading from %s", e, self.name)
                        restring = None

            setattr(instance, f"_{self.name}", self.transform_fun(restring, True))
            setattr(instance, f"_{self.name}_last_poll", time.time())
            return getattr(instance, f"_{self.name}")
        return None
