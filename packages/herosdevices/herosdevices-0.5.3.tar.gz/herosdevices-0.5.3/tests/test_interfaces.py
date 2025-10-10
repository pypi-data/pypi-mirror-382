from src.herosdevices.interfaces.atomiq import Switch
from src.herosdevices.interfaces.heros import ConfiguredDevice
from src.herosdevices.interfaces import UnionInterfaceMeta


def test_has__hero_implements():
    assert hasattr(Switch, "_hero_implements")


def test_has__hero_methods():
    assert hasattr(Switch, "_hero_methods")


def test_interface_union():
    class Dummy(Switch, ConfiguredDevice, metaclass=UnionInterfaceMeta):
        pass

    assert set(Dummy._hero_implements) == {
        "atomiq.components.primitives.Switchable",
        "herosdevices.interfaces.ConfiguredDevice",
    }
    assert set(Dummy._hero_methods) == {"on", "off", "is_on", "get_configuration", "set_configuration", "get_status"}
