"""General drivers for GPIO pins which can be used with the gpiod library."""

from asyncio import AbstractEventLoop
from datetime import timedelta

import gpiod
from heros.event import event

from herosdevices.interfaces.atomiq import Measurable, Switch


class GPIOOutput(Switch):
    """
    A single GPIO configured as output.

    The access to the GPIO is based on libgpiod and thus uses the standard linux kernel interface
    (i.e. /dev/gpiochip* devices).

    Args:
        gpiochip: number of the gpiochip as exposed by the linux kernel.
        pin: number of the GPIO pin
        drive: how to drive the GPIO pin. Possible values: PUSH_PULL (default), OPEN_SOURCE, OPEN_DRAIN
    """

    def __init__(self, gpiochip: int, pin: int, drive: str = "PUSH_PULL") -> None:
        assert isinstance(pin, int), f"GPIO pin '{pin}' should be an integer"
        assert isinstance(gpiochip, int), f"gpiochip '{gpiochip}' should be an integer"

        self.gpio_chip = gpiod.Chip(f"/dev/gpiochip{gpiochip}")
        self.gpio = self.gpio_chip.request_lines(
            consumer="herosGPIO",
            config={
                pin: gpiod.LineSettings(direction=gpiod.line.Direction.OUTPUT, drive=getattr(gpiod.line.Drive, drive)),
            },
        )
        self.pin = pin

    def on(self) -> None:
        """Set GPIO pin to logically active state.

        Default is that active means the pin is high, but the behavior can be changed.
        """
        self.gpio.set_value(self.pin, gpiod.line.Value.ACTIVE)

    def off(self) -> None:
        """Set GPIO pin to logically inactive state.

        Default is that inactive means the pin is low, but the behavior can be changed.
        """
        self.gpio.set_value(self.pin, gpiod.line.Value.INACTIVE)

    def is_on(self) -> bool:
        """Return the current logical state of the GPIO pin (ACTIVE = True, INACTIVE = False)."""
        return self.gpio.get_value(self.pin) == gpiod.line.Value.ACTIVE

    def _observable_data(self) -> bool:
        return self.is_on()


class GPIOInput(Measurable):
    """
    A single GPIO configured as input.

    The access to the GPIO is based on libgpiod and thus uses the standard linux kernel interface
    (i.e. /dev/gpiochip* devices).

    Args:
        gpiochip: number of the gpiochip as exposed by the linux kernel.
        pin: number of the GPIO pin
        bias: bis to apply to the GPIO pin. Possible values: AS_IS (default), DISABLED, PULL_DOWN, PULL_UP, UNKNOWN
        debounce_ms: debouncing time in milliseconds.
        edge_detection: If given it performs the specified edge detection an issues an edge event. Valid values are
            BOTH, FALLING, NONE, RISING. For this to work, an asyncio loop has to given as well.
        loop: asyncio loop in which the edge detection task can be performed. This is required if edge detection is
            set.
        drive: Currently unused.
    """

    def __init__(
        self,
        gpiochip: int,
        pin: int,
        drive: str = "PUSH_PULL",  # noqa: ARG002 TODO: this does nothing. Can it be removed?
        bias: str = "AS_IS",
        debounce_ms: int = 5,
        edge_detection: str = "NONE",
        loop: AbstractEventLoop | None = None,
    ) -> None:
        assert isinstance(pin, int), f"GPIO pin '{pin}' should be an integer"
        assert isinstance(gpiochip, int), f"gpiochip '{gpiochip}' should be an integer"

        self.gpio_chip = gpiod.Chip(f"/dev/gpiochip{gpiochip}")
        self.gpio = self.gpio_chip.request_lines(
            consumer="herosGPIO",
            config={
                pin: gpiod.LineSettings(
                    direction=gpiod.line.Direction.INPUT,
                    bias=getattr(gpiod.line.Bias, bias),
                    edge_detection=getattr(gpiod.line.Edge, edge_detection),
                    debounce_period=timedelta(milliseconds=debounce_ms),
                ),
            },
        )
        self.pin = pin
        self.debounce_ms = debounce_ms

        if edge_detection != "NONE" and loop is not None:
            loop.run_in_executor(None, self._monitor_edge)

    def status(self) -> bool:
        """Get the current input level of the GPIO pin. (True = ACTIVE, False = INACTIVE).

        Default is that active means the pin is high, but the behavior can be changed.
        """
        return self.gpio.get_value(self.pin) == gpiod.line.Value.ACTIVE

    def is_on(self) -> bool:
        """Alias for :py:meth:`status`."""
        return self.status()

    def measure(self, channel: str = "") -> bool:  # noqa: ARG002
        """Alias for :py:meth:`status`."""
        return self.status()

    def _observable_data(self) -> bool:
        """Alias for :py:meth:`status`."""
        return self.status()

    def _monitor_edge(self) -> None:
        """Monitor the GPIO pin for edge events.

        On an observed edge, the :py:meth:`edge_event` event is emitted.
        """
        while True:
            edges = self.gpio.read_edge_events(1)
            if len(edges) > 0:
                self.edge_event(edges[0])

    @event
    def edge_event(self, edge: gpiod.EdgeEvent) -> dict:
        """Emit an HEROS event with the edge event data.

        Returns:
            A dict with the  keys `type` and `timestamp`.
        """
        return {"type": edge.event_type.name, "timestamp": edge.timestamp_ns}
