"""Drivers for Windfreak Technologies devices."""

from collections.abc import Callable
from math import isnan
from typing import Never

from herosdevices.core import DeviceCommandQuantity
from herosdevices.core.templates import SerialDeviceTemplate as SerialDevice
from herosdevices.helper import explicit, limits, limits_int, transform_unit
from herosdevices.interfaces.atomiq import RFSource


class SynthUSB(RFSource, SerialDevice):
    """Base class for Windfreak Synth USB RF generators.

    Not for standalone use, use :py:class:`herosdevice.device.windfreak.SynthUSB2` or
    :py:class:`herosdevice.device.windfreak.SynthUSB3` instead.
    """

    amplitude: float = 0
    freq_max: float = 6.4e9
    freq_min: float = 12.5e6

    status = DeviceCommandQuantity(command_get="?", dtype=str, read_line=False)  # Status overview

    def __init__(self, address: str, timeout: float = 1.0) -> None:
        SerialDevice.__init__(
            self, address, baudrate=19200, timeout=timeout, delays={"read_echo": 0.05}, line_termination=b"\n"
        )

    def _set_frequency(self, frequency: float) -> None:
        self.frequency = frequency

    def _get_frequency(self) -> float:
        return self.frequency

    def _set_amplitude(self, amplitude: int) -> None:
        self.power = amplitude

    def _get_amplitude(self) -> float:
        return self.power

    def _set_phase(self, phase: float) -> None:
        raise NotImplementedError("The Windfreak USBSynth does not support setting a phase")

    def _get_phase(self) -> float:
        raise NotImplementedError("The Windfreak USBSynth does not support setting a phase")


class SynthUSBII(SynthUSB):
    """Windfreak SynthUSB2 RF generator driver."""

    amp_max: float = 3
    amp_min: float = 0

    on: int = DeviceCommandQuantity(
        command_set="o{}", command_get="o?", dtype=int, value_check_fun=explicit([0, 1])
    )  # on/off (0/1)
    high_rf: int = DeviceCommandQuantity(
        command_set="h{}", command_get="h?", dtype=int, value_check_fun=explicit([0, 1]), read_line=True
    )  # High RF on/off (0/1)
    amplitude: int = DeviceCommandQuantity(
        command_set="a{}", command_get="a?", dtype=int, value_check_fun=limits_int(0, 3)
    )  # RF Power int between 0 and 3

    frequency = DeviceCommandQuantity(
        command_set="f{:.3f}",
        command_get="f?",
        dtype=float,
        unit="base",
        value_check_fun=limits(34.4e6, 4.4e9),
        transform_fun=transform_unit("base", "MHz"),
        format_fun=lambda x: float(x.rstrip()) * 1e-3,  # Device returns the value without decimal point...
    )  # Frequency in Hz


class SynthUSBIII(SynthUSB):
    """Windfreak SynthUSB3 RF generator driver."""

    amp_max: float = 10
    amp_min: float = -50

    frequency = DeviceCommandQuantity(
        command_set="f{:.3f}",
        command_get="f?",
        dtype=float,
        unit="base",
        value_check_fun=limits(12.5e6, 5.4e9),
        transform_fun=transform_unit("base", "MHz"),
        format_fun=lambda x: float(x.rstrip()),
    )  # Frequency in Hz

    amplitude = DeviceCommandQuantity(
        command_set="W{}",
        command_get="W?",
        dtype=float,
        unit="dBm",
        value_check_fun=limits(-50, 10),
    )  # RF Power
    doubler = DeviceCommandQuantity(
        command_set="D{}",
        command_get="D?",
        dtype=int,
        unit="dBm",
        value_check_fun=explicit([0, 1]),
    )  # Reference Doubler
    frequency_ramp_lower = DeviceCommandQuantity(
        command_set="l{}",
        command_get="l?",
        dtype=float,
        unit="base",
        value_check_fun=limits(SynthUSB.freq_min, SynthUSB.freq_max),
        transform_fun=transform_unit("base", "MHz"),
    )  # Lower Ramp Limit
    frequency_ramp_upper = DeviceCommandQuantity(
        command_set="u{}",
        command_get="u?",
        dtype=float,
        unit="base",
        value_check_fun=limits(SynthUSB.freq_min, SynthUSB.freq_max),
        transform_fun=transform_unit("base", "MHz"),
    )  # Upper Ramp Limit
    ramp_step_size = DeviceCommandQuantity(
        command_set="s{}", command_get="s?", dtype=float, unit="base", transform_fun=transform_unit("base", "MHz")
    )  # Ramp Step Size
    ramp_step_time = DeviceCommandQuantity(
        command_set="t{}",
        command_get="t?",
        dtype=float,
        unit="ms",
    )  # Dwell time per step
    amplitude_ramp_lower = DeviceCommandQuantity(
        command_set="[{}",
        command_get="[?",
        dtype=float,
        unit="dBm",
        value_check_fun=limits(-50, 10),
    )  # Lower Power Ramp Limit
    amplitude_ramp_upper = DeviceCommandQuantity(
        command_set="]{}",
        command_get="]?",
        dtype=float,
        unit="dBm",
        value_check_fun=limits(-50, 10),
    )  # Upper Power Ramp Limit
    ramp_direction = DeviceCommandQuantity(
        command_set="^{}", command_get="^?", dtype=int, value_check_fun=explicit([0, 1])
    )  # ramp direction 0: upper->lower, 1: lower->upper
    run_sweep = DeviceCommandQuantity(
        command_set="g{}", command_get="g?", dtype=int, value_check_fun=explicit([0, 1])
    )  # controls running a sweep 1:start, restart or continue and 0:pause
    sweep_cont = DeviceCommandQuantity(
        command_set="c{}", command_get="c?", dtype=int, value_check_fun=explicit([0, 1])
    )  # 1:sweep continuously, 0:single sweep

    def ramp(
        self,
        duration: float,
        frequency_start: float = float("nan"),
        frequency_end: float = float("nan"),
        amplitude_start: float = float("nan"),
        amplitude_end: float = float("nan"),
        ramp_timestep: float = float("nan"),
        ramp_steps: int = -1,
    ) -> None:
        """Ramp frequency and amplitude over a given duration.

        Parameters default to ``-1`` or ``nan`` to indicate no change. If the start frequency/amplitude is set
        to ``nan``, the ramp starts from the last frequency/amplitude which was set.
        This method advances the timeline by `duration`

        Args:
            duration: ramp duration [s]
            frequency_start: initial frequency [Hz]
            frequency_end: end frequency [Hz]
            amplitude_start: initial amplitude [0..1]
            amplitude_end: end amplitude [0..1]
            ramp_timesteps: time between steps in the ramp [s]
            ramp_steps: number of steps the whole ramp should have. This takes precedence over `ramp_timesteps`
        """
        self.run_sweep = 0
        if not (isnan(frequency_start) and isnan(frequency_end)) and not (
            isnan(amplitude_start) and isnan(amplitude_end)
        ):
            msg = f"The Windfreak SynthUSB3 {self.address} is not capable parallel frequency/amplitude ramps"
            raise NotImplementedError(msg)

        elif not isnan(frequency_start) or not isnan(frequency_end):
            frequency_start = self.frequency if isnan(frequency_start) else frequency_start
            frequency_end = self.frequency if isnan(frequency_end) else frequency_end
            if frequency_end > frequency_start:
                self.ramp_direction = 1
                self.frequency_ramp_upper = frequency_end
                self.frequency_ramp_lower = frequency_start
            else:
                self.ramp_direction = 0
                self.frequency_ramp_upper = frequency_start
                self.frequency_ramp_lower = frequency_end
        elif not isnan(amplitude_start) or not isnan(amplitude_end):
            amplitude_start = self.amplitude if isnan(amplitude_start) else amplitude_start
            amplitude_end = self.amplitude if isnan(amplitude_end) else amplitude_end
            if amplitude_end > amplitude_start:
                self.ramp_direction = 1
                self.amplitude_ramp_upper = amplitude_end
                self.amplitude_ramp_lower = amplitude_start
            else:
                self.ramp_direction = 0
                self.amplitude_ramp_upper = amplitude_start
                self.amplitude_ramp_lower = amplitude_end

        if isnan(ramp_steps):
            ramp_steps = self.default_ramp_steps
        if not isnan(ramp_timestep):
            pass
        elif ramp_steps > 0:
            ramp_timestep = duration / ramp_steps
        self.ramp_step_time = ramp_timestep
        self.ramp_step_size = abs(amplitude_start - amplitude_end) / ramp_steps

        self.run_sweep = 1
        self.frequency = frequency_end
        self.amplitude = amplitude_end

    def arb(
        self,
        duration: float,
        samples_amp: list[float],
        samples_freq: list[float],
        samples_phase: list[float],
        repetitions: int = 1,
        prepare_only: bool = False,
        run_prepared: bool = False,
        transform_amp: Callable[[float], float] = lambda x: x,
        transform_freq: Callable[[float], float] = lambda x: x,
        transform_phase: Callable[[float], float] = lambda x: x,
    ) -> Never:
        """Play Arbitrary Samples from a List.

        This method is currently not implemented on the Windfreak SynthUSB3. The device would be capable of this and
        drivers can be extended.

        Args:
            samples_amp: List of amplitude samples. If this list is empty (default), the amplitude is not modified.
            samples_freq: List of frequency samples. If this list is empty (default), the frequency is not modified.
            samples_phase: List of phase samples. If this list is empty (default), the phase is not modified.
            duration: The time in which the whole sequence of samples should be played back [s].
            repetitions: Number of times the sequence of all samples should be played. (default 1)
            prepare_only: Only write the sequence to RAM, don't play it.
            run_prepared: Play arb sequence previously prepared with :code:`prepare_only`.
            transform_amp: Function to transform amplitude samples, must take a single argument of type
                :type:`float` and return a single :type:`float`.
            transform_freq: Function to transform frequency samples (see :code:`transform_amp`).
            transform_phase: Function to transform phase samples (see :code:`transform_amp`).
        """
        raise NotImplementedError(
            "Our current driver does not support the arb register functionality of the "
            "SynthUSB3. If you need this, please get in contact with us."
        )
