import pytest
from unittest.mock import patch

from src.herosdevices.core.bus import OneWire


class DummyOneWire(OneWire):
    _observables = [
        ("temp", float, "degC"),
        ("voltage", float, "mV"),
    ]


@pytest.fixture
def mock_read_content():
    def side_effect(path):
        path = str(path)
        if path.endswith("temp"):
            return "23.5"
        elif path.endswith("voltage"):
            return "5000"
        else:
            raise FileNotFoundError(f"Unexpected path: {path}")

    with (
        patch.object(DummyOneWire, "_read_content", side_effect=side_effect),
        patch("os.path.exists", return_value=True),
    ):
        yield


def test_onewire_reads(mock_read_content):
    device = DummyOneWire("28-00000abc")
    data = device._observable_data()
    assert data["temp"] == (23.5, "degC")
    assert data["voltage"] == (5000.0, "mV")
