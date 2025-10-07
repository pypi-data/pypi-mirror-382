"""HEROS drivers for teledyne cameras using the PVCam API."""

import math
import os
import threading
import time
from typing import Any

from heros.helper import log

from herosdevices.core.templates.camera import CameraTemplate

try:
    from pyvcam import constants as pvc_constants  # type: ignore
    from pyvcam import pvc  # type: ignore
    from pyvcam.camera import Camera as PvcCamera  # type: ignore
except ModuleNotFoundError:
    pvc = None
    PvcCamera = None
    pvc_constants = None
    log.exception("Could not import the 'pvcam' python module, required for using teledyne cameras")


DEFAULT_CONFIG = {
    "frame_count": 10,
    "timeout": -1,
    "trigger_delay": 0,
}


class PvcamCamera(CameraTemplate):
    """
    A class to interface with Teledyne PVCam Cameras.

    The class provides functionality to control and capture images from cameras.
    It manages camera configuration, acquisition, and data streaming compatible with the atomiq camera template.

    Args:
        cam_id: Serial number of the cam. Can be obtained for example from the ids-peak GUI. Note, that the id
            is only the first part of the value shown in the GUI, the part including the device type is not
            unique and may not be added to :code:`cam_id`.
        lib_path: Path to vendor library.
        config_dict: Dict of configuration values like shown in the json example above.
        default_config: Default key in :code:`config_dict` to use.

    Note:
        The vendor library must be obtained from the
        `official website <https://www.teledynevisionsolutions.com/products/pvcam-sdk-amp-driver/>`_
        Make sure that after the installation either the environment variable :code:`PVCAM_SDK_PATH` is set to the
        correct path or pass it via the :code:`lib_path` argument.

    Example:
        The class can be started with BOSS with the following example JSON dict::

            {
              "_id": "my-camera",
              "classname": "herosdevices.hardware.teledyne.PvcamCamera",
              "arguments": {
                "cam_id": "pvcamUSB_0",
                "default_config": "default",
                "config_dict": {
                  "default": {
                    "roi": [
                      1500,
                      800,
                      700,
                      700
                    ],
                    "exp_mode": "Edge Trigger"
                  }
                }
              }
            }


        Other than the special config keys listed below, the keys are property names of the pyvcam
        :code:`Camera` object. You can find the full list of available properties sometimes in the pyvcam documentation
        or by crawling `this file <https://github.com/Photometrics/PyVCAM/blob/master/src/pyvcam/camera.py>`_.

    **Special Config Keys:**

    - ``exposure_time``: exposure time in seconds. Automatically sets the nearest resolution (`exp_res` camera
      parameter). If you want to set the `exp_res` attribute manually, use the camera key `exp_time`
      (in the corresponding units) instead of `exposure_time`.
    - ``trigger_delay``: Is added to the trigger delay that can be obtained by :py:attr:`PvcamCamera.trigger_delay`
      and can be used for a cable and camera dependent delay.
    - ``frame_count``: number of frame buffers to set up, `-1` means infinite number of frames. Note, that this is
      currently not supported though. If you need it implemented via a circular buffer, please open an issue or get
      in contact with us.
    - ``post_processing``: A dict of post processing parameters (only if camera supports it), of the form
      :code:`{'feature_name': ['param_name', 'param_value']}`. See the documentation of the camera for details.

    """

    trigger_delay: float | None = None
    _special_config_keys = ["frame_count", "timeout"]  # non peak node map config keys

    def __init__(
        self, cam_id: str, config_dict: dict, default_config: str | None = None, lib_path: str | None = None
    ) -> None:
        self.default_config_dict = DEFAULT_CONFIG
        self.cam_id = cam_id
        if lib_path is not None:
            os.environ["PVCAM_SDK_PATH"] = lib_path
        try:
            pvc.init_pvcam()
        except RuntimeError as e:
            if "PL_ERR_LIBRARY_ALREADY_INITIALIZED" in str(e):
                pass
            else:
                raise
        super().__init__(config_dict, default_config)

    def get_pyvcam_property(self, name: str) -> Any:
        """Read a property value from the underlying pyvcam camera class.

        This is for example useful to get possible
        configuration options for the camera. Possible properties can be found in the source code of the
        `pyvcam driver <https://github.com/Photometrics/PyVCAM/blob/master/src/pyvcam/camera.py>`_.

        Args:
            name: name of the property as defined in the driver
        """
        with self.get_camera() as camera:
            return getattr(camera, name)

    def _open(self) -> PvcCamera:
        """Open camera object. Do not call manually.

        :meta private:
        """
        try:
            camera = PvcCamera(self.cam_id)
            camera.open()
        except RuntimeError as e:
            avail_devices = PvcCamera.get_available_camera_names()
            msg = f"Camera {self.cam_id} not found. Available cameras are: {avail_devices}"
            raise RuntimeError(msg) from e
        return camera

    def _set_config(self, config: dict) -> bool:
        with self.get_camera() as camera:
            camera.reset_pp()
            for key, value in config.items():
                if key == "roi":
                    camera.set_roi(*value)
                elif key == "exposure_time":
                    if value % 1e-3 < 1e-5:  # noqa: PLR2004
                        camera.exp_res = 0  # pass the exposure time in ms
                        camera.exp_time = int(value * 1e3)  # convert from seconds to ms
                    elif value % 1e-6 < 1e-5:  # noqa: PLR2004
                        camera.exp_res = 1  # pass the exposure time in us
                        camera.exp_time = int(value * 1e6)  # convert from seconds to us
                    else:
                        camera.exp_res = 2  # pass the exposure time in s
                        camera.exp_time = int(value)
                elif key == "post_processing":
                    for pkey, pvalue in value.items():
                        camera.set_post_processing_param(pkey, *pvalue)
                elif key not in self._special_config_keys:
                    try:
                        setattr(camera, key, value)
                    except RuntimeError as e:
                        log.error("Failed to set PVCam camera attribute %s to value %s: %s", key, value, e)

        return True

    def _acquisition_loop(self) -> None:
        frame_id = -1
        config = self.get_configuration()
        frame_count = config["frame_count"]
        timeout = config["timeout"]
        metadata = {}

        with self.get_camera() as camera:
            try:
                while not self._stop_acquisition_event.is_set() and (frame_id < frame_count - 1 or frame_count < 0):
                    frame_id += 1
                    time_start = time.time()
                    while not self._stop_acquisition_event.is_set():
                        try:
                            img_array, _, _ = camera.poll_frame(timeout_ms=1000, copyData=False)
                            metadata["frame"] = frame_id
                            self.acquisition_data(img_array["pixel_data"].astype("int16"), metadata)
                            break
                        except RuntimeError:
                            time.sleep(1)
                            if timeout > 0:
                                if timeout < (time.time() - time_start):
                                    log.error("Frame number %s timed out", frame_id)
                                    break
            except RuntimeError as e:
                log.error("Exception occurred in acquisition thread: %s", e)
            self._stop_acquisition_event.set()

            if frame_count > 0:
                if frame_id != frame_count - 1:
                    log.error("Incorrect number of received frames: %s  instead of %s!", frame_id, frame_count)
            self.stop()

    def _arm(self) -> bool:
        self._start_acquisition_thread()
        return True

    def _start_acquisition_thread(self) -> None:
        """Start the acquisition thread."""
        config = self.get_configuration()
        frame_count = config["frame_count"]
        with self.get_camera() as camera:
            try:
                camera.start_seq(num_frames=frame_count)
                self._calculate_trigger_delay()
                camera.start_seq(num_frames=frame_count)
            except Exception as e:  # noqa: BLE001
                log.error("Starting PVCam acquisition failed: %s", e)
        log.debug("Starting acquisition thread")
        self._stop_acquisition_event.clear()
        self._acquisition_thread = threading.Thread(target=self._acquisition_loop)
        self._acquisition_thread.start()

    def _start(self) -> bool:
        with self.get_camera() as camera:
            camera.sw_trigger()
        return True

    def _stop(self) -> bool:
        if self.acquisition_running is False or self._acquisition_thread is None:
            self.acquisition_running = False
            return True

        try:
            self._stop_acquisition_event.set()
            if threading.current_thread().ident != self._acquisition_thread.ident:
                # Kill the datastream to exit out of pending `WaitForFinishedBuffer` calls
                self._acquisition_thread.join()
            else:
                self.acquisition_stopped()
                with self.get_camera() as camera:
                    camera.finish()
            self._acquisition_thread = None
        except Exception as e:  # noqa: BLE001
            log.error("Exception (stop acquisition): %s", str(e))
            return False
        else:
            return True

    def _calculate_trigger_delay(self) -> None:
        """Calculate the trigger delay of the current exposure.

        In this universal driver class here, it only uses the
        user set :code:`trigger_delay` from the configuration dict.
        To include line scan times and the like, it must be implemented on a model to model basis as it strongly
        deviates.
        """
        self.trigger_delay = self.get_configuration()["trigger_delay"]

    def _get_status(self) -> dict:
        return {
            "acquisition_running": self.acquisition_running,
        }

    def _teardown(self) -> None:
        log.debug(f"closing down connection to {self.cam_id}")
        self.stop()
        if self._device is not None:
            self._device.close()

    def __del__(self) -> None:
        """Call teardown method on deletion."""
        self.teardown()


class Kinetix(PvcamCamera):
    """Driver class for the Kinetix camera.

    This class adds the following device specific functionality:

    - The trigger delay stored in the :py:attr:`Kinetix.trigger_delay` is calculated from the user specified trigger
      delay and the delay from the trigger input to the `All Rows` condition.

    For more information refer to :py:class:`PvcamCamera`

    Note:
        It is well possible to that other PVCam cameras that support the fake global shutter concept (e.g. defined
        `All Rows` condition) can also be used with this driver.
    """

    def _calculate_trigger_delay(self) -> None:
        """
        Calculate the delay from trigger input to the "All Rows" condition.

        This can be for example the time you want to switch on a light source.
        This delay is dependent on the read out port and the number of pixel lines used in the exposure.
        More details can be found in the official Kinetix manual.
        The user specified `trigger_delay` config value is added to the returned value. The returned value is in
        units of seconds.
        """
        config = self.get_configuration()
        with self.get_camera() as camera:
            if "roi" in config:
                n_lines = config["roi"][3]
            else:
                # no roi configured -> full sensor
                n_lines = camera.sensor_size[1]
            if camera.readout_port == 0:
                base_delay_num = 2
            else:
                base_delay_num = 1
                n_lines = math.ceil(n_lines / 2) * 2
            try:
                eff_scan_time_ns = camera.scan_line_time * (base_delay_num + camera.scan_line_delay) / 2
                # Somehow only some KINETIX can do a scan line delay
            except AttributeError:
                eff_scan_time_ns = camera.scan_line_time * (base_delay_num) / 2
            scan_time = 1e-9 * eff_scan_time_ns * n_lines
        self.trigger_delay = config["trigger_delay"] + scan_time
