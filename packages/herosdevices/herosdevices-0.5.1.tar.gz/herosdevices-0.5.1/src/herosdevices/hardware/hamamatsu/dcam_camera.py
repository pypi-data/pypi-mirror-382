"""Implementation of the CameraTemplate for Hamamatsu DCAM cameras.

Also see the corresponding section in the documentation.
"""

import threading
import time
from typing import Literal

import numpy as np

from herosdevices.core.templates import CameraTemplate
from herosdevices.helper import log

try:
    import dcamsdk4  # type: ignore
except ModuleNotFoundError:
    log.exception("Could not import the 'dcam' python module, required for using DCAM cameras")
    raise


# example config for Orca Quest C1550-UP
EXAMPLE_CONFIG_DICT = {
    "default": {
        "DCAM_IDPROP.TRIGGERSOURCE": "DCAMPROP.TRIGGERSOURCE.INTERNAL",
        "DCAM_IDPROP.TRIGGERPOLARITY": "DCAMPROP.TRIGGERPOLARITY.POSITIVE",
        "DCAM_IDPROP.EXPOSURETIME": 0.01,
        "DCAM_IDPROP.SENSORMODE": "DCAMPROP.SENSORMODE.AREA",
        # "DCAM_IDPROP.BINNING": DCAMPROP.BINNING._1,
        "DCAM_IDPROP.BINNING": "DCAMPROP.BINNING._4",
        "DCAM_IDPROP.SUBARRAYHSIZE": 200,
        "DCAM_IDPROP.SUBARRAYVSIZE": 200,
        "DCAM_IDPROP.SUBARRAYHPOS": 4 * 34,
        "DCAM_IDPROP.SUBARRAYVPOS": 4 * 117,
        "DCAM_IDPROP.SUBARRAYMODE": "DCAMPROP.MODE.ON",
    }
}


def generate_dcam_error_dict() -> dict:
    """
    Get a dictionary that maps numerical error code against human-readable string.

    Returns:
        Dictionary of error codes -> error descriptions
    """
    out_dict = {}
    for error in dir(dcamsdk4.DCAMERR):
        if not error.startswith("__"):
            attr = getattr(dcamsdk4.DCAMERR, error)
            if hasattr(attr, "value"):  # in v24 they have added methods to the DCAMERR enum :|
                out_dict.update({attr.value: error})
    return out_dict


def get_prop_or_val(prop_str: str = "DCAMPROP.TRIGGERSOURCE.SOFTWARE") -> int | float:
    """
    Get a dictionary that maps numerical error code against human-readable string.

    Args:
        prop_str: Property of interest

    Returns:
        Value of the property of interest

    """
    if not isinstance(prop_str, str):
        log.spam(f"{prop_str} is no instance of str")
        return prop_str
    out = dcamsdk4
    for attr in prop_str.split("."):
        try:
            out = getattr(out, attr)
        except AttributeError as e:
            msg = f"Error resolving {prop_str}: {out} has no attribute {attr}"
            raise RuntimeError(msg) from e
    log.spam(f"Resolved {prop_str} to {out.value}")
    return out.value


def validate_roi(val: int, binning: int = 1) -> int:
    """
    Calculate a valid ROI size of position with a given binning setting.

    Args:
        val: ROI size or position value
        binning: number of pixels to bin in one direction (1, 2, 4)

    Returns:
        Valid ROI size or position correwcted with binning
    """
    return val - val % (4 * binning)


class DcamCompatibleCamera(CameraTemplate):
    """
    Camera object for Hamamatsu DCAM cameras.

    In particular, this code has been tested with the C15550-20UP.
    """

    _special_config_keys = ["frame_count", "timeout"]  # non-DCAM props
    default_config_dict: dict = {}

    def _raise_for_status(
        self, val: float | bool, camera_handle: None = None, do_raise: bool = True
    ) -> int | float | bool:
        """
        Check if an API call failed and raise the error, else return the return value.

        Args:
            val: API call return value
            camera_handle: Camera handle or None
            do_raise: Set to False if this method should only log the error

        Returns:
            Returned value of the API call

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        if (not val) and isinstance(val, bool):
            error_dict = generate_dcam_error_dict()
            if camera_handle is None:
                last_error_str = "DCAM SDK error without initialized camera"
            else:
                last_error = camera_handle.lasterr()
                if last_error in error_dict:
                    last_error_str = error_dict[last_error]
                else:
                    last_error_str = repr(last_error)
            log.error(last_error_str)
            if do_raise:
                msg = f"DCAM error: {last_error_str}"
                raise RuntimeError(msg)
        return val

    def set_property(self, prop: str, value: str) -> bool:
        """
        Set a single property on the device.

        Args:
            prop: Property of interest
            value: Target value

        Returns:
            True if setting the property was successful

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        try:
            attr_name = get_prop_or_val(prop)
            attr_value = get_prop_or_val(value)
            with self.get_camera() as camera:
                self._raise_for_status(camera.prop_setvalue(attr_name, attr_value), camera)
        except RuntimeError as ex:
            log.error(f"Could not set {prop} to {value}: {ex}")
            return False
        return True

    def get_property(self, prop: str) -> int | float | None:
        """
        Read a single property from the device and reports its value.

        Args:
            prop: Property of interest

        Returns:
            Value of the property

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        _prop = get_prop_or_val(prop)
        with self.get_camera() as camera:
            try:
                prop_val = self._raise_for_status(camera.prop_getvalue(_prop), camera)
            except RuntimeError as ex:
                log.error(f"could not read {prop}: {ex}")
                return None
            # try to resolve, else just report the bare value
            try:
                return self._raise_for_status(camera.prop_getvaluetext(_prop, prop_val), camera)
            except RuntimeError:
                return prop_val

    def get_propperty_dict(self, prop_dict: dict | None = None) -> dict:
        """
        Read a dictionary of properties and report their value.

        Args:
            prop_dict: A dict of properties (as strings)

        Returns:
            A dict oft property values

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        # TODO: Why do we need prop_dict as an optional arg? The function does nothing if left out....
        if prop_dict is None:
            prop_dict = {}
        out = {}
        for return_name, prop in prop_dict.items():
            out[return_name] = self.get_property(prop)
        return out

    def get_temperature(self) -> dict:
        """
        Get cooling and temperature properties.

        Returns:
            A dict of sensor temperature, cooler status

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        props = {
            "sensor_temperature": "DCAM_IDPROP.SENSORTEMPERATURE",
            "sensor_cooler_mode": "DCAM_IDPROP.SENSORCOOLER",
            "sensor_cooler_status": "DCAM_IDPROP.SENSORCOOLERSTATUS",
        }
        return self.get_propperty_dict(props)

    def get_acquisition_mode(self) -> dict:
        """
        Get SENSORMODE, READOUTSPEED and BINNING properties.

        Returns:
            A dict of SENSORMODE, READOUTSPEED and BINNING

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        props = {
            "sensor_mode": "DCAM_IDPROP.SENSORMODE",
            "sensor_readoutspeed": "DCAM_IDPROP.READOUTSPEED",
            "sensor_binning": "DCAM_IDPROP.BINNING",
        }
        return self.get_propperty_dict(props)

    def get_timing_infos(self) -> dict:
        """
        Get trigger timing properties.

        Returns:
            A dict of trigger timing properties

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        props = {
            "cyclic trigger period": "DCAM_IDPROP.TIMING_CYCLICTRIGGERPERIOD",
            "min trigger blanking": "DCAM_IDPROP.TIMING_MINTRIGGERBLANKING",
            "internal frame interval": "DCAM_IDPROP.INTERNAL_FRAMEINTERVAL",
            "timing readout time": "DCAM_IDPROP.TIMING_READOUTTIME",
        }
        return self.get_propperty_dict(props)

    def get_all_properties(self) -> list[tuple]:
        """Dump all properties from the device.

        Copied from demo scripts.

        Returns:
            A list with all camera properties known to DCAM.
        """
        output_list = []
        with self.get_camera() as camera:
            idprop = camera.prop_getnextid(0)
            while idprop is not False:
                prop_hex = f"0x{idprop:08X}: "
                prop_name = camera.prop_getname(idprop)
                prop_val = camera.prop_getvalue(idprop)
                log.info(f"{prop_hex} (prop_name): {prop_val}")
                output_list.append((prop_hex, prop_name, prop_val))
                # get next prop
                idprop = camera.prop_getnextid(idprop)
        return output_list

    # methods to overwrite CameraTemplate
    def _open(self) -> dcamsdk4.Dcam:
        """Open the camera handler with the first device ID connected to the system."""
        self._raise_for_status(dcamsdk4.Dcamapi.init())
        log.spam("Camera object created")
        # TODO make device configurable
        cam_id = dcamsdk4.Dcamapi.get_devicecount() - 1
        log.info(f"Camera id: {cam_id}")
        camera = self._raise_for_status(dcamsdk4.Dcam(cam_id))
        self._raise_for_status(camera.dev_open())
        log.debug("Camera opened")
        return camera

    def _teardown(self) -> None:
        """Release the camera handler and de-initialize the API."""
        try:
            with self.get_camera() as camera:
                self._raise_for_status(camera.dev_close(), camera, do_raise=False)
        except Exception as e:  # noqa: BLE001
            # this captures other strange non-DCAM errors
            log.error(e)
        finally:
            log.debug("Closing API")
            dcamsdk4.Dcamapi.uninit()

    def _start(self) -> bool:
        """
        Fire a software trigger via DCAM.

        Returns:
            True if successful

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        with self.get_camera() as camera:
            return self._raise_for_status(camera.cap_firetrigger(), camera)

    def _stop(self) -> Literal[True]:
        """Abort the exposure and release queued buffers."""
        with self.get_camera() as camera:
            try:
                self._stop_acquisition_thread()
                self._raise_for_status(camera.cap_stop(), camera, do_raise=False)
            except Exception as e:  # noqa: BLE001
                log.error(e)
            finally:
                self._raise_for_status(camera.buf_release(), camera, do_raise=False)
            return True

    def _get_status(self) -> dict:
        """
        Get a dict with the current device status.

        Returns:
            A dict with the device status

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        status = {}
        for query in [self.get_temperature, self.get_acquisition_mode, self.get_timing_infos]:
            status.update(query())
        return status

    def _set_config(self, config: dict) -> bool:
        """Configure camera features.

        ROI size and position need to be adjusted based on the binning setting.

        Args:
            config: A valid configuration dict passed from :meth:`set_config`

        Returns:
            True if configuration is possible

        Raises:
            RuntimeError: last error in case the API call returned False
        """
        t0 = time.time()
        if "DCAM_IDPROP.BINNING" in config:
            # translate the binning settings into an int by getting the prop from DCAM
            binning = int(get_prop_or_val(config["DCAM_IDPROP.BINNING"]))
        else:
            binning = 1
        log.debug(f"Binning: {binning}")
        # calculate valid ROIs
        if "DCAM_IDPROP.SUBARRAYMODE" in config:
            for key in [
                "DCAM_IDPROP.SUBARRAYHPOS",
                "DCAM_IDPROP.SUBARRAYVPOS",
                "DCAM_IDPROP.SUBARRAYHSIZE",
                "DCAM_IDPROP.SUBARRAYVSIZE",
            ]:
                if key in config:
                    config[key] = int(validate_roi(config[key], binning))
                    log.debug(f"Calculated valid pixel pos or size {key}: {config[key]}")
        # set properties
        with self.get_camera() as camera:
            for prop_name, prop_val in config.items():
                if prop_name in self._special_config_keys:
                    # skip non-DCAM props
                    continue
                attr_name = get_prop_or_val(prop_name)
                attr_value = get_prop_or_val(prop_val) if isinstance(prop_val, str) else prop_val
                try:
                    log.spam(f"Setting: {attr_name}, {attr_value}")
                    self._raise_for_status(camera.prop_setvalue(attr_name, attr_value), camera)
                except RuntimeError as ex:
                    log.error(f"Error in setting and getting attribute {prop_name}: {ex}")
                    self.teardown()
                    return False
        t1 = time.time()
        log.debug(f"Configuration completed in {(t1 - t0) * 1e3:.0f}ms")
        return True

    def _arm(self) -> bool:
        """
        Arm the camera with the currently active configuration.

        Returns:
            True if arming was successful else False
        """
        try:
            frame_count = self.config_dict[self._config]["frame_count"]
            log.info(f"Arming camera for {frame_count} frames")
            with self.get_camera() as camera:
                self._raise_for_status(camera.buf_alloc(frame_count), camera)
                self._raise_for_status(camera.cap_start(False), camera)  # True: SEQUENCE mode, False: SNAP mode
            self._start_acquisition_thread()
        except RuntimeError:
            log.exception("Error while arming camera:")
            return False
        return True

    # code for the image acquisition
    def _start_acquisition_thread(self) -> None:
        """Start the acquisition thread."""
        log.debug("Starting acquisition thread")
        self._stop_acquisition_event.clear()
        self._acquisition_thread = threading.Thread(target=self._acquisition_loop)
        self._acquisition_thread.daemon = False  # daemon thread?
        self._acquisition_thread.start()
        self.acquisition_running = True
        self.acquisition_started(self.get_configuration())

    def _stop_acquisition_thread(self) -> None:
        """Stop the acquisition thread and wait for it to terminate."""
        if self._acquisition_thread is not None:
            # set the stop event and mark acquisition as not running
            self._stop_acquisition_event.set()
            self.acquisition_running = False
            # join the thread to wait for its termination
            frame_timeout = self.config_dict[self._config]["timeout"]
            self._acquisition_thread.join(timeout=1.1 * frame_timeout)
            # check if the thread is still alive
            if self._acquisition_thread.is_alive():
                log.warn("Acquisition thread did not terminate gracefully")
            else:
                log.debug("Acquisition thread stopped successfully")
                self._acquisition_thread = None
                self.acquisition_running = True

    def _acquisition_loop(self) -> None:
        """Grab all images from queued buffers and release buffers."""
        images = []
        frame_count = self.config_dict[self._config]["frame_count"]
        frame_timeout_millis = int(self.config_dict[self._config]["timeout"] * 1e3)
        # the camera has to be open here since it is armes
        # since we need to access the device while it is used here (wait_capevent_frameready),
        # we directly use self._device - circumventing the context manager
        # otherwise we would not be able to use the software trigger (self.start()) or abort the exposure
        camera = self._device
        for i in range(frame_count):
            # check if we need to stop
            if self._stop_acquisition_event.is_set():  # Check stop event with timeout
                return
            log.debug(f"Waiting for frame {i + 1} (frame id {i}) / {frame_count}")
            try:
                self._raise_for_status(camera.wait_capevent_frameready(frame_timeout_millis), camera)
                log.debug("Got data")
                image = np.array(camera.buf_getframedata(i), dtype=np.uint16)
                images.append(image)
                # emit image via event
                self.acquisition_data(image, {"frame": i})
            except Exception as e:  # noqa: BLE001
                if isinstance(e, RuntimeError):
                    log.error(f"Dcam CameraError during acquisition: {e}")
                else:
                    log.error(f"Unhandled error during acquisition: {e}")
        # here, we again use the context manager
        with self.get_camera() as camera:
            log.debug("Stopping exposure")
            self._raise_for_status(camera.cap_stop(), camera, do_raise=False)
            log.debug("Releasing buffer")
            self._raise_for_status(camera.buf_release(), camera, do_raise=False)
        # cleanup
        self._acquisition_thread = None
        self.acquisition_running = False
        self.acquisition_stopped({"frames": len(images), "frame_count": frame_count})
        if len(images) != frame_count:
            log.error(f"Incorrect number of received frames: {len(images)} instead of {frame_count}!")
            self.reset()
