"""Helper functions for writing hardware drivers."""

import logging
import re
from collections.abc import Callable
from typing import Any

##############################################################
# extend logging mechanism
SPAM = 5
setattr(logging, "SPAM", 5)  # noqa: B010 #TODO: Why is this line necessary at all?
logging.addLevelName(levelName="SPAM", level=5)


class Logger(logging.Logger):
    """Extend logger to include a spam level for debugging device communication."""

    def setLevel(self, level: str | int, globally: bool = False) -> None:  # noqa: N802 D102
        if isinstance(level, str):
            level = level.upper()
        try:
            level = int(level)
        except ValueError:
            pass
        logging.Logger.setLevel(self, level)
        if globally:
            for logger in logging.root.manager.loggerDict.values():
                if not hasattr(logger, "setLevel"):
                    continue
                logger.setLevel(level)

    def spam(self, msg: str, *args, **kwargs) -> None:
        """Log a message with severity SPAM, even lower than DEBUG."""
        self.log(SPAM, msg, *args, **kwargs)


logging.setLoggerClass(Logger)
format_str = "%(asctime)-15s %(name)s: %(message)s"
logging.basicConfig(format=format_str)

log = logging.getLogger("herosdevices")


SI_PREFIX_EXP = {
    "Y": 24,
    "Z": 21,
    "E": 18,
    "P": 15,
    "T": 12,
    "G": 9,
    "M": 6,
    "k": 3,
    "h": 2,
    "base": 0,
    "d": -1,
    "c": -2,
    "m": -3,
    "u": -6,
    "n": -9,
    "p": -12,
    "f": -15,
    "a": -18,
    "z": -21,
    "y": -24,
}


def limits(lower: float, upper: float) -> Callable[[float], str | bool]:
    """Create a function which checks if a value is within the specified range.

    Args:
        lower: The lower bound of the valid range.
        upper: The upper bound of the valid range.

    Returns:
        A function that takes a value and returns True if within the range, or a message
        indicating it's out of range.
    """

    def check(val: float) -> str | bool:
        if val < lower or val > upper:
            return f"Value {val} is out of range [{lower}, {upper}]"
        return True

    return check


def limits_int(lower: int, upper: int) -> Callable[[int], str | bool]:
    """Create a function to check if a value is within a specified range and is an integer.

    Args:
        lower: The lower bound of the valid range.
        upper: The upper bound of the valid range.

    Returns:
        A function that takes a value and returns True if within the range and is an integer,
        or a message indicating why it's invalid.
    """

    def check(val: int) -> str | bool:
        if val < lower or val > upper:
            return f"Value {val} is out of range [{lower}, {upper}]"
        if val % 1 != 0:
            return f"Value {val} is not an integer"
        return True

    return check


def explicit(values: list[Any]) -> Callable[[Any], str | bool]:
    """Create a function to check if a value is in a list of allowed values.

    Args:
        values: A list of allowed values.

    Returns:
        A function that takes a value and returns True if within the list, or a message
        indicating it's not in the list.
    """

    def check(val: Any) -> bool | str:
        if val not in values:
            return f"Value {val} is not in list of allowed values {values}"
        return True

    return check


def extract_regex(pattern: str) -> Callable[[str], str]:
    """Create a function to extract a value from a string via regex pattern matching.

    Args:
        regex: regex pattern string.

    Returns:
        A function that takes a string and returns the first match group.
    """

    def match_str(input_string: str) -> str:
        match = re.search(pattern, input_string)

        if match:
            return match.group()
        return ""

    return match_str


def transform_unit(in_unit: str, out_unit: str) -> Callable[[float, bool], float]:
    """Create a function to transform a value from one unit to another using SI prefixes.

    Args:
        in_unit: The input unit (e.g., 'k' for kilo, 'm' for milli). Use 'base' for no prefix.
        out_unit: The output unit (e.g., 'k' for kilo, 'm' for milli). Use 'base' for no prefix.

    Returns:
        A function that transforms a given value from the input unit to the output unit,
        optionally allowing reverse transformation (second argument True).
    """
    if in_unit == "base":
        in_exp = 0
    else:
        in_exp = SI_PREFIX_EXP[in_unit[0]]
    if out_unit == "base":
        out_exp = 0
    else:
        out_exp = SI_PREFIX_EXP[out_unit[0]]
    multiplier = 10 ** (in_exp - out_exp)

    def transform(val: float, reverse: bool = False) -> float:
        if reverse:
            return val / multiplier
        return val * multiplier

    return transform


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Recursively merge two dicts of dicts."""
    new_dict = dict1.copy()
    for k, v in dict2.items():
        if k in dict1 and isinstance(dict1[k], dict) and isinstance(v, dict):
            new_dict[k] = merge_dicts(new_dict[k], v)
        else:
            new_dict[k] = v
    return new_dict


def add_class_descriptor(cls: type, attr_name: str, descriptor) -> None:  # noqa: ANN001
    """
    Add a descriptor to a class.

    This is a simple helper function which uses `setattr` to add an attribute to the class and then also calls
    `__set_name__` on the attribute.

    Args:
        cls: Class to add the descriptor to
        attr_name: Name of the attribute the descriptor will be added to
        descriptor: The descriptor to be added
    """
    setattr(cls, attr_name, descriptor)
    getattr(cls, attr_name).__set_name__(cls, attr_name)
