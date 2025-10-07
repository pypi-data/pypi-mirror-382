from src.herosdevices.core.templates.acq_device import AcquisitionDeviceTemplate
import pytest

default_config = {
    "default": {
        "val": "test",
        "ch0": {
            "coupling": 0,
        },
    }
}

default_metadata = {"path": "test", "nested": {"val": 1}}


@pytest.fixture
def instance():
    AcquisitionDeviceTemplate.default_config_dict = {"val": "false", "val2": "test"}
    obj = AcquisitionDeviceTemplate(config_dict=default_config, payload_metadata=default_metadata)
    return obj


def test_update_config(instance):
    assert instance.get_configuration() == {"val2": "test"} | default_config["default"]

    new_conf = dict(test=default_config["default"], default={"val": "test2"})
    instance.update_configuration(new_conf)
    assert instance.get_configuration() == {"val2": "test"} | default_config["default"] | {"val": "test2"}
    instance.configure("test")
    assert instance.get_configuration() == {"val2": "test"} | default_config["default"]


def test_update_metadata(instance):
    assert instance.payload_metadata == default_metadata

    instance.configure("default", metadata={"nested": {"val": 2, "val2": 1}})
    assert instance.payload_metadata == {"path": "test", "nested": {"val": 2, "val2": 1}}

    instance.update_payload_metadata(default_metadata, merge=False)
    assert instance.payload_metadata == default_metadata

    instance.update_payload_metadata(metadata={"nested": {"val": 2, "val2": 1}})
    assert instance.payload_metadata == {"path": "test", "nested": {"val": 2, "val2": 1}}
