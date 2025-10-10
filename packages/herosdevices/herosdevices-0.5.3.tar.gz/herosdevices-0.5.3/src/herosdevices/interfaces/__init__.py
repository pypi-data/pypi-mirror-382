"""This module includes interfaces which are used to describe capabilities of devices."""

from heros.inspect import force_remote


class Interface:
    """Generic Interface to describe and check capabilities of a device driver."""

    _hero_methods: list[str] = []
    _hero_implements: list[str] = []

    def __init__(self) -> None:
        for method_name in self._hero_methods:
            if hasattr(self, method_name):
                if method_name.startswith("_"):
                    setattr(self.__class__, method_name, force_remote(getattr(self.__class__, method_name)))
            else:
                msg = (
                    f"Method with name '{method_name}' not found in class {self.__class__.__name__} but required "
                    f"for at least one interface in {self._hero_implements}"
                )
                raise NotImplementedError(msg)


class UnionInterfaceMeta(type):
    """This metaclass is used to correctly unify the implementation attributes during multiple inheritance.

    The _heros_implements and _hero_methods attributes are combined from all base classes.

    .. caution::
        This is not meant to be inherited from directly but used with the `metaclass` keyword.
    """

    def __new__(metacls, name: str, bases: tuple, namespace: dict) -> "UnionInterfaceMeta":
        """Combine all '_heros_implements' from base classes."""
        combined_implements = set()
        combined_methods = set()
        for base in bases:
            base_hero_implements = getattr(base, "_hero_implements", [])
            base_hero_methods = getattr(base, "_hero_methods", [])
            combined_implements.update(base_hero_implements)
            combined_methods.update(base_hero_methods)
        namespace["_hero_implements"] = list(combined_implements)
        namespace["_hero_methods"] = list(combined_methods)
        return super().__new__(metacls, name, bases, namespace)
