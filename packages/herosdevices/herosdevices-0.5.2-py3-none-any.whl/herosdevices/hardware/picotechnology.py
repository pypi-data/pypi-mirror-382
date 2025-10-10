"""Driver classes for Pico Technology Ltd. devices."""

import ctypes
import math
import threading
import time

import numpy as np
from heros.helper import log

from herosdevices.core.templates.oscilloscope import OscilloscopeTemplate

PICO_CHANNEL_FLAGS = [1, 2, 4, 8, 16, 32, 64, 128]


PICO_RANGE = {
    "PICO_10MV": 0,
    "PICO_20MV": 1,
    "PICO_50MV": 2,
    "PICO_100MV": 3,
    "PICO_200MV": 4,
    "PICO_500MV": 5,
    "PICO_1V": 6,
    "PICO_2V": 7,
    "PICO_5V": 8,
    "PICO_10V": 9,
    "PICO_20V": 10,
}


DEFAULT_CONFIG = {
    "resolution": "PICO_DR_8BIT",
    "channel_default": {
        "coupling": "PICO_DC",
        "range": "PICO_10V",
        "bandwidth": "PICO_BW_FULL",
        "offset": 0.0,
        "record_trace": True,
    },
    "trigger": {"source": 0, "threshold": 1.0, "type": "PICO_RISING", "delay": 0, "auto_trig_time": 0},
    "acquisition": {"sample_time": 1e-6, "trace_length": 100e-6, "n_blocks": 1, "downsampling": "PICO_RATIO_MODE_RAW"},
    "trace_count": float("inf"),
}


try:
    import picosdk.functions as pico_functions  # type: ignore
    from picosdk.constants import PICO_STATUS  # type: ignore
    from picosdk.PicoDeviceEnums import picoEnum  # type: ignore
    from picosdk.ps6000a import ps6000a  # type: ignore
except ModuleNotFoundError:
    log.exception("Could not import the 'picosdk' python module, required for using pico oscilloscopes")
    ps6000a = None
    picoEnum = None  # noqa: N816
    pico_functions = None
    PICO_STATUS = None


class Picoscope(OscilloscopeTemplate):
    """A class to interface Pico Technology computer oscilloscopes.

    This is the base class for the different models and can not be used standalone. Please refer to the specific
    model drivers.
    """

    _resolution_bit: int = 0
    _scope: ctypes.c_int16
    _adc_lims: tuple[ctypes.c_int16, ctypes.c_int16] = (ctypes.c_int16(), ctypes.c_int16())

    def __init__(
        self,
        serial_num: str,
        config_dict: dict,
        default_config: str | None = None,
        **kwargs,
    ) -> None:
        """Create instance of a Picoscope representation.

        Args:
            serial_num: Serial number of the picoscope. You can get that from the PicoScope GUI, it looks something
                like this: `JP402/0012`
            config_dict: Dict of configuration values like shown in the json examples of the individual picoscope
                model drivers.
            default_config: Default key in :code:`config_dict` to use.
            **kwargs: Additional keyword arguments are passed to
                :py:class:`herosdevices.core.templates.oscilloscope.OscilloscopeTemplate`

        Note:
            You need the official picoscope sdk installed. Note that it is not on PyPi and you need to follow the
            instructions :ref:`here<https://github.com/picotech/picosdk-python-wrappers>`
        """
        self.serial_num: str = serial_num
        self._record_channels: list[int] = []
        self._enabled_channels: list[int] = []
        self.default_config_dict = DEFAULT_CONFIG
        super().__init__(config_dict, default_config, **kwargs)

    def assert_status(self, result: int) -> None:
        """Check if a command result was successful.

        Args:
            result: Returnvalue from a picoscope command.

        Raises:
            AssertionError: If the result is not ``PICO_OK``.
        """
        assert result == PICO_STATUS["PICO_OK"], list(PICO_STATUS.keys())[list(PICO_STATUS.values()).index(result)]

    def _start(self) -> bool:
        raise NotImplementedError("Picoscopes do not support manual trigger")
        return False

    def _get_status(self) -> dict:
        return {"acquisition_running": self.acquisition_running}


class Picoscope6000a(Picoscope):
    """
    Driver class for the Picoscope 6000 series.

    Note:
        You need the official picoscope sdk installed. Note that it is not on PyPi and you need to follow the
        instructions `here <https://github.com/picotech/picosdk-python-wrappers>`_

    Example:
        The class can be started with BOSS with the following example JSON dict::

            {
              "_id": "myscope",
              "classname": "herosdevices.hardware.picotechnology.Picoscope6000a",
              "arguments": {
                "serial_num": "JP306/0102",
                "default_config": "default",
                "config_dict": {
                  "default": {
                    "ch0": {
                      "coupling": "PICO_DC_50OHM",
                      "range": "PICO_100MV"
                    },
                    "ch1": {
                      "coupling": "PICO_DC_50OHM",
                      "range": "PICO_5V",
                      "record_trace": false
                    },
                    "trigger": {
                      "source": 1,
                      "threshold": 1.5
                    },
                    "acquisition": {
                      "trace_length": 0.000006,
                      "sample_time": 2e-10
                    }
                  }
                }
              }
            }

    """

    def _open(self) -> ctypes.c_int16:
        handle = ctypes.c_int16()
        self.assert_status(ps6000a.ps6000aOpenUnit(ctypes.byref(handle), None, self._resolution_bit))
        return handle

    def _set_config(self, config: dict) -> bool:
        self._record_channels = []
        self._enabled_channels = []
        with self.get_scope() as scope:
            if "resolution" in config:
                try:
                    resolution_bit = picoEnum.PICO_DEVICE_RESOLUTION[config["resolution"]]
                    if resolution_bit != self._resolution_bit:
                        # resolution is set on open, reopen necessary
                        self.teardown()
                        self._resolution_bit = resolution_bit
                        self.open()
                except KeyError:
                    log.error(
                        "%s is not a valid vertical resolution for any PicoScope, ignoring...",
                        [
                            config["resolution"],
                        ],
                    )

            for i_channel in range(4):
                if f"ch{i_channel}" in config:
                    channel_config = config["channel_default"] | config[f"ch{i_channel}"]
                    self.assert_status(
                        ps6000a.ps6000aSetChannelOn(
                            scope,
                            i_channel,
                            picoEnum.PICO_COUPLING[channel_config["coupling"]],
                            PICO_RANGE[channel_config["range"]],
                            channel_config["offset"],
                            picoEnum.PICO_BANDWIDTH_LIMITER[channel_config["bandwidth"]],
                        )
                    )
                    if channel_config["record_trace"]:
                        self._record_channels.append(i_channel)
                    self._enabled_channels.append(i_channel)
                else:
                    self.assert_status(ps6000a.ps6000aSetChannelOff(scope, i_channel))

            source = config["trigger"]["source"]
            if source == -1:
                source = picoEnum.PICO_CHANNEL["PICO_TRIGGER_AUX"]

            self.assert_status(
                ps6000a.ps6000aGetAdcLimits(
                    scope,
                    self._resolution_bit,
                    ctypes.byref(self._adc_lims[0]),
                    ctypes.byref(self._adc_lims[1]),
                )
            )
            try:
                trigger_channel_settings = config["channel_default"] | config[f"ch{source}"]
            except KeyError:
                log.error(
                    "Trying to set channel %s as trigger source, but is disabled. Trigger is not configured.",
                    [
                        source,
                    ],
                )
            else:
                source_range = PICO_RANGE[trigger_channel_settings["range"]]
                threshold = config["trigger"]["threshold"] * 1000
                self.assert_status(
                    ps6000a.ps6000aSetSimpleTrigger(
                        scope,
                        1,
                        source,
                        pico_functions.mV2adc(threshold, source_range, self._adc_lims[1]),
                        picoEnum.PICO_THRESHOLD_DIRECTION[config["trigger"]["type"]],
                        # TODO: is currently in sample intervals: needs to be in seconds,
                        config["trigger"]["delay"],
                        config["trigger"]["auto_trig_time"],
                    )
                )
        return True

    def _prepare_block_capture(
        self,
        pre_trigger_samples: int,
        post_trigger_samples: int,
    ) -> tuple[list[list[ctypes.Array[ctypes.c_int16]]], list[list[ctypes.Array[ctypes.c_int16]]]]:
        """Prepare the oscilloscope for a block capture sequence.

        Args:
            timebase: See manual how timebase is calculated. Can be calculated with ps6000aGetTimebase
            downsampling: Any of PICO_RATIO_MODE, if None: PICO_RATIO_MODE["PICO_RATIO_MODE_RAW"]
            n_segments: number of segments the memory should be partitioned to
        """
        config = self.get_configuration()
        n_segments = config["acquisition"]["n_blocks"]
        downsampling = picoEnum.PICO_RATIO_MODE[config["acquisition"]["downsampling"]]
        n_samples = pre_trigger_samples + post_trigger_samples
        buffer_max = [[(ctypes.c_int16 * n_samples)() for _ in range(n_segments)] for _ in self._record_channels]
        buffer_min = [[(ctypes.c_int16 * n_samples)() for _ in range(n_segments)] for _ in self._record_channels]

        data_type = picoEnum.PICO_DATA_TYPE["PICO_INT16_T"]

        with self.get_scope() as scope:
            self.assert_status(
                ps6000a.ps6000aMemorySegments(
                    scope,
                    n_segments,
                    ctypes.byref(ctypes.c_uint64(n_segments)),
                )
            )
            self.assert_status(ps6000a.ps6000aSetNoOfCaptures(scope, n_segments))
            action = picoEnum.PICO_ACTION["PICO_CLEAR_ALL"] | picoEnum.PICO_ACTION["PICO_ADD"]
            for i_channel, channel in enumerate(self._record_channels):
                for i_block in range(n_segments):
                    self.assert_status(
                        ps6000a.ps6000aSetDataBuffers(
                            scope,
                            channel,
                            ctypes.byref(buffer_max[i_channel][i_block]),
                            ctypes.byref(buffer_min[i_channel][i_block]),
                            n_samples,
                            data_type,
                            i_block,
                            downsampling,
                            action,
                        )
                    )
                    action = picoEnum.PICO_ACTION["PICO_ADD"]

            return buffer_max, buffer_min

    def _acquisition_loop(self) -> None:
        trace_id = 0
        timebase = ctypes.c_uint32(0)
        time_interval = ctypes.c_double(0)
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        overflow = ctypes.c_int16(0)

        config = self.get_configuration()
        trace_count = config["trace_count"]
        n_segments = config["acquisition"]["n_blocks"]
        metadata = {}
        metadata["data_columns"] = ["time (s)"]
        metadata["data_columns"].extend([f"ch{i}_{j}" for i in self._record_channels for j in range(n_segments)])

        with self.get_scope() as scope:
            self._set_config(self.get_configuration())
            self.assert_status(
                ps6000a.ps6000aNearestSampleIntervalStateless(
                    scope,
                    sum([(x**2) + 1 for x in self._enabled_channels]),
                    config["acquisition"]["sample_time"],
                    self._resolution_bit,
                    ctypes.byref(timebase),
                    ctypes.byref(time_interval),
                )
            )
            pre_trigger_samples = math.ceil(config["trigger"]["delay"] / time_interval.value)
            post_trigger_samples = math.ceil(
                (config["acquisition"]["trace_length"] - config["trigger"]["delay"]) / time_interval.value
            )
            n_samples = pre_trigger_samples + post_trigger_samples
            time_array = np.linspace(0, (n_samples - 1) * time_interval.value * 1000000000, n_samples)

            buffers = self._prepare_block_capture(
                pre_trigger_samples,
                post_trigger_samples,
            )

            traces = np.empty((n_segments, len(self._record_channels) + 1, n_samples))
            traces[:, 0] = time_array
            while not self._stop_acquisition_event.is_set() and trace_id < trace_count - 1:
                self.assert_status(
                    ps6000a.ps6000aRunBlock(
                        scope,
                        pre_trigger_samples,
                        post_trigger_samples,
                        timebase,
                        ctypes.byref(ctypes.c_double(0)),
                        0,
                        None,
                        None,
                    )
                )

                ready = ctypes.c_int16(0)
                while ready.value == check.value:
                    self.assert_status(ps6000a.ps6000aIsReady(scope, ctypes.byref(ready)))
                    if self._stop_acquisition_event.is_set():
                        break
                    time.sleep(0.01)

                if self._stop_acquisition_event.is_set():
                    break

                for i_channel, channel in enumerate(self._record_channels):
                    overflow = (ctypes.c_int16 * n_segments)()
                    self.assert_status(
                        ps6000a.ps6000aGetValuesBulk(
                            scope,
                            0,
                            ctypes.byref(ctypes.c_uint64(n_samples)),
                            0,
                            n_segments - 1,
                            1,
                            picoEnum.PICO_RATIO_MODE[config["acquisition"]["downsampling"]],
                            ctypes.byref(overflow),
                        )
                    )

                    channel_config = config["channel_default"] | config[f"ch{channel}"]
                    for i_segment in range(n_segments):
                        traces[i_segment, i_channel + 1] = pico_functions.adc2mV(
                            buffers[0][i_channel][i_segment],
                            PICO_RANGE[channel_config["range"]],
                            self._adc_lims[1],
                        )

                metadata["frame"] = trace_id
                self.acquisition_data(np.array(traces), metadata)
                trace_id += 1

            if trace_count != float("inf"):
                if trace_id != trace_count - 1:
                    log.error("Incorrect number of received frames: %s  instead of %s!", trace_id, trace_count)
            self.stop()

    def _arm(self) -> bool:
        log.debug("Starting acquisition thread")
        self._stop_acquisition_event.clear()
        self._acquisition_thread = threading.Thread(target=self._acquisition_loop)
        self._acquisition_thread.start()
        return True

    def _stop(self) -> bool:
        if self.acquisition_running is False or self._acquisition_thread is None:
            self.acquisition_running = False
            return True
        try:
            if threading.current_thread().ident != self._acquisition_thread.ident:
                # Kill the datastream to exit out of pending `WaitForFinishedBuffer` calls
                self._stop_acquisition_event.set()
                self._acquisition_thread.join()

            self.acquisition_stopped()
            self._acquisition_thread = None

        except Exception as e:  # noqa:BLE001
            log.error("Exception (stop acquisition): %s", str(e))
            return False
        return True

    def _teardown(self) -> None:
        self.stop()
        ps6000a.ps6000aCloseUnit(self._device)
        self._device = None
