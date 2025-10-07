"""Rigol Devices."""

import threading

import numpy as np
import pyvisa
from pyvisa.resources.resource import Resource

from herosdevices.core.templates.oscilloscope import OscilloscopeTemplate
from herosdevices.helper import log


class RigolDSA(OscilloscopeTemplate):
    """
    A class to interface Rigol digital spectrum analyzers.

    Args:
        address: Address or IP of the instrument.
        **kwargs: Additional keyword arguments are passed to
            :py:class:`herosdevices.core.templates.oscilloscope.OscilloscopeTemplate`

    Note:
        Currently, this driver only implements retrieving the current trace and getting the marker positions.
    """

    MAX_MARKERS: int = 4

    def __init__(
        self,
        address: str,
        **kwargs,
    ) -> None:
        self.address: str = address
        self.default_config_dict = {}
        super().__init__(config_dict={"default": {}}, **kwargs)
        # initialize pyvisa resource manager
        self._pyvisa_rm: pyvisa.ResourceManager | None = None
        self.open()

    def _start(self) -> bool:
        raise NotImplementedError("Rigol DSA do not support manual trigger")
        return False

    def _stop(self) -> bool:
        raise NotImplementedError("Rigol DSA do not support manual stopping (yet)")
        return False

    def _set_config(self, config: dict) -> bool:  # noqa: ARG002
        """
        Set a config dictionary on the device.

        Note:
            Currently, this driver does not implement configuring the device.
        """
        return False

    def _get_status(self) -> dict:
        return {
            "acquisition_running": self.acquisition_running,
            "idn": self.get_identification(),
        }

    def _open(self) -> Resource:
        log.info(f"Connecting to {self.address}")
        self._pyvisa_rm = pyvisa.ResourceManager("@py")
        return self._pyvisa_rm.open_resource(f"TCPIP0::{self.address}::INSTR")

    def _teardown(self) -> None:
        try:
            self._device.close()
        except pyvisa.errors.Error:
            log.exception("Error while closind DSA.")
        try:
            self._pyvisa_rm.close()
        except pyvisa.errors.Error:
            log.exception("Error while closing pyvisa resource manager.")

    def _acquisition_loop(self) -> None:
        with self.get_scope() as sa:
            # get trace as ASCII CSV
            sa.write(":FORM:DATA ASCII")  # set ASCII mode
            raw = sa.query(":TRAC:DATA? TRACE1")
            # remove any leading/trailing whitespace or newlines
            raw = raw.strip()
            # if the device adds a leading '#' or count
            if raw.startswith("#"):
                # skip SCPI-style length header
                raw = raw[2 + int(raw[1]) :]  # '#' + digit-count + digits
            # now parse
            trace = np.fromstring(raw, sep=",")
            start_freq = float(sa.query(":FREQ:STAR?"))
            stop_freq = float(sa.query(":FREQ:STOP?"))
            metadata = {
                "start_freq": start_freq,
                "stop_freq": stop_freq,
                "frame": 0,
            }
        self.acquisition_stopped()
        self.acquisition_data(trace, metadata)

    def _arm(self) -> bool:
        log.debug("Starting acquisition thread")
        self._stop_acquisition_event.clear()
        self._acquisition_thread = threading.Thread(target=self._acquisition_loop)
        self._acquisition_thread.start()
        return True

    def get_identification(self) -> str:
        """
        Query the device identification.

        Returns:
            Device identification string.
        """
        with self.get_scope() as sa:
            return sa.query("*IDN?")

    def get_markers(self) -> dict:
        """
        Query all markers from the Rigol spectrum analyzer.

        Returns:
            Dictionary with :code:`{marker_number: (freq_Hz, amp_dBm)}`.
        """
        markers = {}
        with self.get_scope() as sa:
            for i in range(1, self.MAX_MARKERS + 1):
                try:
                    state = int(sa.query(f":CALC:MARK{i}:STAT?").strip())
                except pyvisa.errors.Error:
                    # in case the instrument doesn't support more markers, break
                    break
                if state == 1:
                    freq = float(sa.query(f":CALC:MARK{i}:X?"))
                    amp = float(sa.query(f":CALC:MARK{i}:Y?"))
                    markers[i] = (freq, amp)
        return markers

    def _observable_data(self) -> dict:
        """
        Implement method :meth:`_observable_data` s.t. this class can be used as a :code:`PolledLocalDatasourceHERO`.

        Returns:
            Dictionary with marker positions and amplitudes.
        """
        out = {}
        for i, (freq, amp) in self.get_markers().items():
            out[f"marker_{i}_frequency"] = (freq, "Hz")
            out[f"marker_{i}_amplitude"] = (amp, "dBm")
        return out
