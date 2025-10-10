"""Dummy camera devices for use in testing. Do not use in production."""

import threading

import numpy as np
from numpy.typing import NDArray

from herosdevices.core.templates import CameraTemplate
from herosdevices.helper import log


class ImageGeneratorDummy:
    """Act like a real camera, no one will notice."""

    def __init__(self) -> None:
        self.width = 800
        self.height = 600
        self.frame_count = 1
        self._is_armed = False
        self._image_buffer = []

    def set_shape(self, width: int = 800, height: int = 600) -> None:
        """Set the image shape."""
        self.width = width
        self.height = height

    @staticmethod
    def generate_gaussian_image(
        w: int, h: int, amplitude: float = 65535, noise_level: float = 0.05
    ) -> NDArray[np.unit16]:
        """Generate a 2D Gaussian image with added random noise.

        The Gaussian is centered in the image with a fixed standard deviation,
        scaled to the specified amplitude. Additive Gaussian noise is applied
        and the result is clipped to the valid `uint16` range.

        Args:
            w: Width of the image.
            h: Height of the image.
            amplitude: Peak value of the Gaussian. Defaults to 65535.
            noise_level: Standard deviation of noise relative to
                the amplitude (e.g., 0.05 means ±5% noise). Defaults to 0.05.

        Returns:
            np.ndarray: A (h, w) image array of dtype `np.uint16`.
        """
        x = np.linspace(-1, 1, w)
        y = np.linspace(-1, 1, h)
        xv, yv = np.meshgrid(x, y)
        sigma = 0.3
        gaussian = np.exp(-(xv**2 + yv**2) / (2 * sigma**2))
        gaussian *= amplitude
        noise = np.random.default_rng().normal(loc=0, scale=noise_level * amplitude, size=(h, w))
        image = gaussian + noise
        image = np.clip(image, 0, 65535)
        return image.astype(np.uint16)

    def arm(self) -> None:
        """Arm the dummy device."""
        self._is_armed = True

    def trigger(self) -> None:
        """Append an image to the buffer."""
        if self._is_armed:
            if len(self._image_buffer) == self.frame_count:
                raise RuntimeError("Camera was armed and triggered while buffer was full!")
            self._image_buffer.append(self.generate_gaussian_image(self.width, self.height))
            # did we reach the max frame count?
            if len(self._image_buffer) == self.frame_count:
                self._is_armed = False

    def get_image(self) -> np.ndarray:
        """Get the last image from the buffer."""
        if len(self._image_buffer) > 0:
            return self._image_buffer.pop(0)
        raise RuntimeError("Image buffer empty!")

    def clear_buffer(self) -> None:
        """Clear the image buffer."""
        self._image_buffer = []

    def abort(self) -> None:
        """Abort the acquisition."""
        self._is_armed = False
        self.clear_buffer()


class CameraDummy(CameraTemplate):
    """A dummy camera."""

    _auto_trigger: bool = True
    default_config_dict: dict = {}

    def _open(self) -> ImageGeneratorDummy:
        """Device specific code to open the camera handler and return it."""
        return ImageGeneratorDummy()

    def _teardown(self) -> None:
        """Device specific code to release the camera handler and potentially de-initialize the API."""

    def _start(self) -> bool:
        """
        Device specific code to fire a software trigger via DCAM.

        Returns:
            True if successful
        """
        with self.get_camera() as camera:
            camera.trigger()
        return True

    def _stop(self) -> bool:
        """
        Device specific code to abort the exposure and release queued buffers.

        Returns:
            True if successful
        """
        self._stop_acquisition_thread()
        with self.get_camera() as camera:
            camera.abort()
            camera.clear_buffer()
        return True

    def _get_status(self) -> dict:
        """
        Device specific code to get a dict with the current device status.

        Returns:
            A dict with the device status
        """
        return {"foo": "bar"}

    def _set_config(self, config: dict) -> bool:
        """
        Device specific code to configure camera features.

        Args:
            config: A valid configuration dict passed from :meth:`set_config`

        Returns:
            True if configuration is possible
        """
        with self.get_camera() as camera:
            camera.set_shape(config["height"], config["width"])
        return True

    def _arm(self) -> bool:
        """
        Device specific code to arm the camera with the currently active configuration.

        Returns:
            True if arming was successful else False
        """
        try:
            with self.get_camera() as camera:
                camera.frame_count = self.get_configuration()["frame_count"]
                camera.arm()
            self._start_acquisition_thread()  # has to be implement for the specific device
        except Exception as e:  # noqa: BLE001
            log.error(e)
            return False
        return True

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
            self._acquisition_thread.join(timeout=1)
            # check if the thread is still alive
            if self._acquisition_thread.is_alive():
                log.warn("Acquisition thread did not terminate gracefully")
            else:
                log.debug("Acquisition thread stopped successfully")
                self._acquisition_thread = None
                self.acquisition_running = False

    def _acquisition_loop(self) -> None:
        """Grab all images from queued buffers and release buffers."""
        images = []
        frame_count = self.get_configuration()["frame_count"]
        with self.get_camera() as camera:
            for i in range(frame_count):
                # check if we need to stop
                if self._stop_acquisition_event.is_set():  # Check stop event with timeout
                    return
                log.debug(f"Waiting for frame {i} / {frame_count}")
                if self._auto_trigger:
                    camera.trigger()
                image = camera.get_image()
                images.append(image)
                # emit image via event
                self.acquisition_data(image, {"frame": i})
            log.debug("Stopping exposure")
            camera.clear_buffer()
        # cleanup
        self._acquisition_thread = None
        self.acquisition_running = False
        self.acquisition_stopped({"frames": len(images), "frame_count": frame_count})
        if len(images) != frame_count:
            log.error(f"Incorrect number of received frames: {len(images)} instead of {frame_count}!")
            self.reset()
