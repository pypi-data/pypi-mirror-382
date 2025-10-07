"""Translation/implementation interfaces for HEROized atomiq devices."""

from typing import Any

from heros.event import event

from . import Interface


class AtomiqInterface(Interface):
    """
    This interface defines the necessary methods for a HERO to seamlessly being converted into an atomiq component.

    The methods that need to be implemented are listed in the class-level list `_atomiq_methods`. If a subclass does
    not implement one of these methods a NotImplementedError is raised.

    Important: The methods given here are just the minimal set. Any other method of the atomiq component can be
               overloaded as well. In particular, if your hardware supports ramping or arbitrary functions,
               implement the `ramp()` and/or `arb()` methods in your subclass.
    """


class Switch(AtomiqInterface):
    """HERO implementation of :external+atomiq:py:class:`atomiq.components.primitives.Switchable`."""

    _hero_implements = ["atomiq.components.primitives.Switchable"]
    _hero_methods = ["on", "off", "is_on"]


class Measurable(AtomiqInterface):
    """HERO implementation of :external+atomiq:py:class:`atomiq.components.primitives.Measurable`."""

    _hero_implements = ["atomiq.components.primitives.Measurable"]
    _hero_methods = ["measure"]


class RFSource(AtomiqInterface):
    """HERO implementation of :external+atomiq:py:class:`atomiq.components.electronics.rfsource.RFSource`."""

    _hero_implements = ["atomiq.components.electronics.rfsource.RFSource"]
    _hero_methods = ["_set_amplitude", "_set_frequency", "_set_phase"]

    frequency: float = 1e6
    amplitude: float = 0.1
    phase: float = 0.0
    freq_max: float = 100e6
    freq_min: float = 100e3
    amp_max: float = 1.0
    amp_min: float = 0.0
    default_ramp_steps: int = 30
    blind: bool = False

    @event
    def _observable_data(self) -> list[tuple[str, Any, str]]:
        return [
            ("frequency", self.frequency, "Hz"),
            ("amplitude", self.amplitude, "total"),
            ("phase", self.phase, "rad"),
        ]


class VoltageSource(AtomiqInterface):
    """HERO implementation of :external+atomiq:py:class:`atomiq.components.electronics.voltagesource.VoltageSource`."""

    _hero_implements = ["atomiq.components.electronics.voltagesource.VoltageSource"]
    _hero_methods = ["_set_voltage"]

    min_voltage: float = float("-inf")
    max_voltage: float = float("inf")
    default_ramp_steps: int = 30
    blind: bool = False


class CurrentSource(AtomiqInterface):
    """HERO implementation of :external+atomiq:py:class:`atomiq.components.electronics.currentsource.CurrentSource`."""

    _hero_implements = ["atomiq.components.electronics.currentsource.CurrentSource"]
    _hero_methods = ["_set_current"]

    min_current: float = float("-inf")
    max_current: float = float("inf")
    default_ramp_steps: int = 30
    blind: bool = False


class ADCChannel(AtomiqInterface):
    """HERO implementation of :external+atomiq:py:class:`atomiq.components.electronics.adc.ADCChannel`."""

    _hero_implements = ["atomiq.components.electronics.adc.ADCChannel"]
    _hero_methods = ["measure"]


class Camera(AtomiqInterface):
    """HERO implementation of :external+atomiq:py:class:`atomiq.components.optoelectronics.camera.Camera`."""

    _hero_implements = ["atomiq.components.optoelectronics.camera.Camera"]
    _hero_methods = ["configure", "arm", "start", "stop"]
