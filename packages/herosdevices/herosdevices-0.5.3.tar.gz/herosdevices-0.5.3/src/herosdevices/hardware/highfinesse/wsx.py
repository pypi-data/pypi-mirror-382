"""Device driver for Highfinesse WSx series wavelength meters."""
import ctypes
import os


class WSx:
    """A Highfinesse WSx series wavelength meter.

    Tested with WS6 and WS7.

    Hardware driver to communicate with a High Finesse WSx Wavemeter via the DLL in present in Windows systems with
    the vendor software installed.
    """

    def __init__(self,
                 dll_path: str = r"C:\Windows\System32\wlmData.dll",
                 wavemeter_index: int = 0,
                 channels: tuple = tuple(range(8))
                 ) -> None:
        """
        Initialize the Highfinesse device driver.

        Args:
            dll_path: location of the wlmData.dll
            wavemeter_index: select specific wavemeter out of all connected. (hint: you may use `version` property to
            figure out the correct index
            channels: indices of the channels that should be available
        """
        # access DLL and specify return types
        assert os.name == "nt", "The Highfinesse driver can only run in Windows OS"
        self.dll = ctypes.WinDLL(dll_path) # type: ignore[attr-defined]
        self.wavemeter_index = wavemeter_index

        self.dll.GetWavelengthNum.restype = ctypes.c_double
        self.dll.GetFrequencyNum.restype = ctypes.c_double
        self.dll.GetTemperature.restype = ctypes.c_double
        self.dll.GetExposureNum.restype = ctypes.c_long
        self.dll.SetExposureNum.restype = ctypes.c_long
        self.dll.GetExposureModeNum.restype = ctypes.c_bool
        self.dll.SetExposureModeNum.restype = ctypes.c_long
        self.dll.GetExposureRange.restype = ctypes.c_long
        self.dll.GetSwitcherMode.restype = ctypes.c_long
        self.dll.SetSwitcherMode.restype = ctypes.c_long
        self.dll.GetSwitcherSignalStates.restype = ctypes.c_long
        self.dll.SetSwitcherSignalStates.restype = ctypes.c_long
        self.dll.GetWLMVersion.restype = ctypes.c_long
        self.dll.PresetWLMIndex.restype = ctypes.c_long

        self._select_wavemeter(wavemeter_index=self.wavemeter_index)

        self.channels = channels

    def _select_wavemeter(self, wavemeter_index: int | None = None) -> bool | int:
        if wavemeter_index is None:
            wavemeter_index = self.wavemeter_index
        err = self.dll.PresetWLMIndex(ctypes.c_long(wavemeter_index))
        if err == 0:
            return True
        return err

    @property
    def version(self) -> dict:
        """
        Retrieve model, version, and software version from the device.

        Returns:
            dict: dictionary with keys model, version, software_revision
        """
        return {"model": f"WS{self.dll.GetWLMVersion(ctypes.c_long(0))}",
                "version": self.dll.GetWLMVersion(ctypes.c_long(1)),
                "software_revision": self.dll.GetWLMVersion(ctypes.c_long(2))
                }

    def get_wavelength(self, channel: int = 1) -> float:
        """
        Read the measured light wavelength at the given channel.

        Args:
            channel: channel to be read (if wavemeter is in switch mode)

        Returns:
            float: vac wavelength in nm, if channel is not used or underexposed returns -3,
                if channel is overexposed returns -4
        """
        assert channel in range(1, 9, 1), f"Channel should be in [1,..8], not {channel}"
        return self.dll.GetWavelengthNum(ctypes.c_long(channel), ctypes.c_double(0))

    def get_frequency(self, channel: int = 1) -> float | int:
        """
        Read the measured light frequency at the given channel.

        Args:
            channel: channel to be read (if wavemeter is in switch mode)

        Returns:
            float: frequency in THz, if channel is not used or underexposed returns -3,
                         if channel is overexposed returns -4
        """
        assert channel in range(1, 9, 1), f"Channel should be in [1,..8], not {channel}"
        return self.dll.GetFrequencyNum(ctypes.c_long(channel), ctypes.c_double(0))

    @property
    def temperature(self) -> float:
        """Read temperature of the wavemeter's internal temperature sensor."""
        return self.dll.GetTemperature(ctypes.c_double(0))

    def get_exposure_time(self, channel: int = 1) -> int:
        """
        Read exposure time of the given channel.

        Args:
            channel: channel for which to read the exposure time (if wavemeter is in switch mode)

        Returns:
            int: exposure time in milliseconds
        """
        assert channel in range(1, 9, 1), f"Channel should be in [1,..8], not {channel}"
        return self.dll.GetExposureNum(ctypes.c_long(channel), ctypes.c_long(1), ctypes.c_long(0))

    def set_exposure_time(self, exposure_time: int, channel: int = 1, arr: int = 1) -> bool | int:
        """
        Set the exposure time of the given channel.

        Args:
            channel: channel for which to set the exposure time (if wavemeter is in switch mode)
            arr: which sensor to set the exposure time for

        Returns:
            bool|int: success of the operation. Negative integers indicate errors.
        """
        assert channel in range(1, 9, 1), f"Channel should be in [1,..8], not {channel}"
        assert arr in [1, 2], f"Array should be in [1,2], not {arr}"
        min_exposure, max_exposure = self.get_exposure_range(arr=arr)
        assert exposure_time >= min_exposure, f"ExposureTime should be larger than {exposure_time}, not {min_exposure}"
        assert exposure_time <= max_exposure, f"ExposureTime should be smaller than {exposure_time}, not {max_exposure}"
        err = self.dll.SetExposureNum(ctypes.c_long(channel), ctypes.c_long(arr), ctypes.c_long(exposure_time))
        if err == 0:
            return True
        return err

    def get_auto_exposure_mode(self, channel: int = 1) -> bool:
        """
        Get the status of the automatic exposure time setting.

        Args:
            channel: channel for which to get the automatic exposure time setting (if wavemeter is in switch mode)

        Returns:
            bool: state of the automatic exposure time setting.
        """
        assert channel in range(1, 9, 1), f"Channel should be in [1,..8], not {channel}"
        return self.dll.GetExposureModeNum(ctypes.c_long(channel), ctypes.c_bool(False))

    def set_auto_exposure_mode(self, enable: bool, channel: int = 1) -> bool | int:
        """
        Set the status of the automatic exposure time setting.

        Args:
            channel: channel for which to set the automatic exposure time setting (if wavemeter is in switch mode)

        Returns:
            bool|int: success of the operation. Negative integers indicate errors.
        """
        assert channel in range(1, 9, 1), f"Channel should be in [1,..8], not {channel}"
        assert isinstance(enable, bool), f"Enable should be of type boolean, not {type(enable)}"
        err = self.dll.SetExposureModeNum(ctypes.c_long(channel), ctypes.c_bool(enable))
        if err == 0:
            return True
        return err

    def get_exposure_range(self, arr: int = 1) -> tuple[int, int]:
        """
        Get the possible range of exposure times for the given array/sensor.

        Args:
            arr: array/sensor for which to get the possible exposure times

        Returns:
            tuple(int): minimum and maximum exposure time
        """
        assert arr in [1, 2], f"Array should be in [1,2], not {arr}"
        min_exposure = self.dll.GetExposureRange(ctypes.c_long(2 * arr - 2))
        max_exposure = self.dll.GetExposureRange(ctypes.c_long(2 * arr - 1))
        return min_exposure, max_exposure

    @property
    def switch_mode(self) -> bool:
        """Get state of the multiplex switcher."""
        return self.dll.GetSwitcherMode(ctypes.c_long(0))

    @switch_mode.setter
    def switch_mode(self, enable: bool) -> bool|int:
        assert isinstance(enable, bool)
        err = self.dll.SetSwitcherMode(ctypes.c_long(enable))
        if err == 0:
            return True
        return err

    def get_switcher_signal_state(self, channel: int = 1) -> int|tuple[bool, bool]:
        """Retrieve the status of the "use" and "show" options of the defined channel.

        Args:
            channel: channel for which to get the "use" and "show" state.

        Returns:
            tuple(bool): state of the switches in the form (use, show).
        """
        assert channel in range(1, 9, 1), f"Channel should be in [1,..8], not {channel}"
        use = ctypes.c_long(0)
        show = ctypes.c_long(0)
        err = self.dll.GetSwitcherSignalStates(ctypes.c_long(channel), ctypes.byref(use), ctypes.byref(show))
        if err == 0:
            return (bool(use.value), bool(show.value))
        return err

    def set_switcher_signal_state(self, use: bool, show: bool, channel: int = 1) -> bool|int:
        """Set the status of the "use" and "show" options of the defined channel.

        Args:
            use: state to set for the "use" switch.
            show: state to set for the "show" switch.
            channel: channel for which to set the "use" and "show" state.

        Returns:
            bool|int: success of the operation. Negative integers indicate errors.

        """
        assert isinstance(use, bool), f"use should be of type boolean, not {type(use)}"
        assert isinstance(show, bool), f"show should be of type boolean, not {type(show)}"
        assert channel in range(1, 9, 1), f"Channel should be in [1,..8], not {channel}"
        err = self.dll.SetSwitcherSignalStates(ctypes.c_long(channel), ctypes.c_long(use), ctypes.c_long(show))
        if err == 0:
            return True
        return err

    def set_target_wavelength_vacuum(self, wavelength: float, channel: int = 1) -> bool | int:
        """
        Set the target vacuum wavelength, i.e. if a laser is stabilized to the wavemeter.

        Args:
            wavelength: wavelength to set as target wavelength
            channel:  channel for which to set the target wavelength.

        Returns:
            bool|int: success of the operation. Negative integers indicate errors.
        """
        assert channel in range(1, 9, 1), f"Channel should be in [1,..8], not {channel}"
        err = self.dll.SetPIDCourseNum(ctypes.c_long(channel),
                                       ctypes.c_char_p(f"{wavelength*1e9:.9f}".encode()))
        if err == 0:
            return True
        return err

    def _observable_data(self) -> dict:
        data = {
            "switchMode": (self.switch_mode, ""),
            "temperature": (self.temperature, "degC")
        }
        for channel in self.channels:
            switcher_signal = self.get_switcher_signal_state(channel)
            if not isinstance(switcher_signal, tuple):
                continue
            if not switcher_signal[0]:
                continue
            data[f"channel{channel}.frequency"] = (self.get_frequency(channel), "THz")
            data[f"channel{channel}.wavelength"] = (self.get_wavelength(channel), "nm")
            data[f"channel{channel}.exposureTime"] = (self.get_exposure_time(channel), "ms")
        return data
