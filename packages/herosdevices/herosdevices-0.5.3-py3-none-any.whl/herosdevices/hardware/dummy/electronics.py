"""Dummy low level electronics for use in testing. Do not use in production."""

from herosdevices.helper import log
from herosdevices.interfaces import atomiq


class RFSourceDummy(atomiq.RFSource):
    """Dummy class implementing an atomiq compatible RF source."""

    def _set_amplitude(self, amp: float) -> None:
        log.debug(f"setting amplitude to {amp}")

    def _set_frequency(self, frequency: float) -> None:
        log.debug(f"setting frequency to {frequency}")

    def _set_phase(self, phase: float) -> None:
        log.debug(f"setting phase to {phase}")


class VoltageSourceDummy(atomiq.VoltageSource):
    """Dummy class implementing an atomiq compatible voltage source."""

    def _set_voltage(self, voltage: float) -> None:
        log.debug(f"setting voltage to {voltage}")


class CurrentSourceDummy(atomiq.CurrentSource):
    """Dummy class implementing an atomiq compatible current source."""

    def _set_current(self, current: float) -> None:
        log.debug(f"setting voltage to {current}")


class ADCChannelDummy(atomiq.ADCChannel):
    """Dummy class implementing a single atomiq compatible ADC channel."""

    def measure(self, samples: int = 1, cached: bool = False, channel: str = "") -> float:
        """'Meaure' a fake voltage."""
        del channel, cached, samples
        return 3.14


class SwitchDummy(atomiq.Switch):
    """Dummy class implementing an atomiq compatible switch."""

    _state: bool = False

    def on(self) -> None:
        """Set the switch state to True."""
        self._state = True
        log.debug("Switch turned on")

    def off(self) -> None:
        """Set the switch state to False."""
        self._state = False
        log.debug("Switch turned off")

    def is_on(self) -> bool:
        """Return the current switch state."""
        return self._state
