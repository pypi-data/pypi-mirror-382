"""Template for general acquisition devices like cameras and oscilloscopes."""

import threading
from abc import abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import numpy as np
from heros import event

from herosdevices.helper import log, merge_dicts
from herosdevices.interfaces import UnionInterfaceMeta
from herosdevices.interfaces.heros import ConfiguredDevice


class AcquisitionDeviceTemplate(ConfiguredDevice, metaclass=UnionInterfaceMeta):
    """
    Template (base class) for acquisition-like devices.

    Template for devices which are based on the concept of configuring the device first and
    then running an acquisition thread which collects data (like images, osci traces,...).

    To make a functional device driver, the user needs to implement all abstract methods.
    In addition, this call does not cover the mechanism the actually retrieve the data
    from the device since it is typically special to each vendor/API. A general guideline
    should be to start a separate thread for the acquisition which uses the _acquisition_lock
    to prohibit concurrent exposures. For each received data set, the event :meth:`acquisition_data`
    should be called. In addition, :meth:`acquisition_stopped` should be emitted
    after the acquisition.

    The driver must also define the `default_config_dict` attribute, intended for configuration values which are applied
    to all user configurations if the corresponding keys are not specified.
    """

    _special_config_keys: list | tuple = ()
    acquisition_running: bool = False
    payload_metadata: dict
    default_config_dict: dict

    def __init__(
        self,
        config_dict: dict,
        default_config: str | None = None,
        keep_device_open: bool = True,
        payload_metadata: dict | None = None,
    ) -> None:
        """
        Create a new device object.

        Args:
            config_dict: Configuration dictionary, see EXAMPLE_CONFIG
            default_configuration: Default (starting) configuration
            keep_device_open: Keep the device open after it is first opened
        """
        self.keep_device_open = keep_device_open
        self._device = None
        self._acquisition_thread: threading.Thread | None = None
        self._acquisition_lock = threading.Lock()  # lock to ensure single exposure at a time
        self._stop_acquisition_event = threading.Event()  # event to signal the thread to stop

        self._config_dict: dict = {}
        self.update_configuration(config_dict)
        self.default_config: str = default_config if default_config is not None else "default"
        self._config: str = self.default_config
        self.configure()  # configure with default config

        self.payload_metadata: dict = payload_metadata if payload_metadata is not None else {}

    @contextmanager
    def get_device(self) -> Iterator[None]:
        """
        Yield a device handle.

        .. code-block:: python

            # use the device in a with statement
            with self.get_device() as camera:
                camera.do_something()
        """
        log.spam("Requesting device")
        if self._device is None:
            self.open()
        yield self._device
        if not self.keep_device_open:
            self.teardown()

    def open(self) -> Any:
        """Open the device handler and assign it to `self._device`."""
        log.info("Opening device handler")
        self._device = self._open()

    def teardown(self) -> None:
        """Release the device handler and potentially de-initialize the API."""
        log.info("Closing device")
        self._teardown()
        self._device = None

    __del__ = teardown

    def start(self) -> bool:
        """
        Fire a software trigger.

        Returns:
            True if successful
        """
        log.info("Firing software trigger")
        return self._start()

    def stop(self) -> bool:
        """
        Abort the exposure and release queued buffers.

        Returns:
            True if successful
        """
        log.error("Aborting any exposure")
        return self._stop()

    def reset(self) -> None:
        """Reset the device by aborting any ongoing exposure, closing and re-opening the handler."""
        log.error("Resetting device")
        self.stop()
        self.teardown()
        try:
            self.open()
            self.configure()
        except Exception as e:  # noqa: BLE001
            log.warn(f"Opening and configuration during reset failed: {e}")

    def get_status(self) -> dict:
        """
        Get a dict with the current device status.

        Returns:
            A dict with the device status
        """
        status = {
            "acquisition_running": self.acquisition_running,
        }
        # add device specific status
        status.update(self._get_status())
        return status

    @property
    def config_dict(self) -> dict:
        """
        Get a copy of the configuration dict.

        Returns:
            Copy of the configuration dict
        """
        return {**self._config_dict}

    def update_configuration(self, new_config_dict: dict, merge: bool = True) -> None:
        """
        Update the configuration dict with new configuration.

        Each dict key corresponds a (new) configuration name.
        Each value is a dict with config property -> config value.

        Args:
            new_config_dict: A dict of configurations where the keys are the configuration names
            merge: If ``True``, the new dict is recursively merged with the current set config dict. If ``False`` the
                old configurations with the provided names (keys) are overwritten.
        """
        # finally update config
        if merge:
            self._config_dict = merge_dicts(self._config_dict, new_config_dict)
        else:
            # check if special config keyes are present
            for config_name, config in new_config_dict.items():
                for key in self._special_config_keys:
                    assert key in config, f"Required config key {key} not found in config {config_name}!"
            self._config_dict.update(new_config_dict)
            # check if special config keyes are present
            for config_name, config in new_config_dict.items():
                for key in self._special_config_keys:
                    assert key in config, f"Required config key {key} not found in config {config_name}!"

    def get_configuration(self) -> dict:
        """
        Get the currently active configuration.

        Returns:
            The currently active configuration.
        """
        return merge_dicts(self.default_config_dict, self.config_dict[self._config])

    def configure(self, config: str = "", metadata: dict | None = None) -> bool:
        """
        Configure the device with the known configuration `config`.

        To add a configuration to the device, use :meth:`update_configuration`.

        Args:
            config: Key (name) of the configuration
            metadata: Metadata that is merged into the current payload metadata dict which is send with every emitted
                :code:`acquisition_data` event.
        """
        if config == "":
            self._config = self.default_config
        else:
            self._config = config
        log.debug(f"Configuring device with setting key: {self._config}")
        with self._acquisition_lock:  # acquire lock s.t. no acquisition can start
            if self.acquisition_running:
                log.error("Cannot configure device while the acquisition is running!")
                return False
            self._set_config(self.get_configuration())

        if metadata is not None:
            self.update_payload_metadata(metadata)
        return True

    set_configuration = configure  # satisfy interface requirement

    def update_payload_metadata(self, metadata: dict, merge: bool = True) -> None:
        """Update metadata dict send with every emitted frame by the :code:`acquisition_data` event method.

        Args:
            metadata: Metadata that is merged into the current payload metadata dict which is send with every emitted
                :code:`acquisition_data` event.
            merge: If ``True``, the new dict is merged with the current set metadata dict. If ``False`` the old
                metadata is overwritten by the given dict.
        """
        if merge:
            self.payload_metadata = merge_dicts(self.payload_metadata, metadata)
        else:
            self.payload_metadata = metadata

    def arm(self, metadata: dict | None = None, kill_running: bool = False) -> bool:
        """
        Arm the device with the currently active configuration.

        Args:
            metadata: Metadata that is merged into the current payload metadata dict which is send with every emitted
                :code:`acquisition_data` event.
            kill_running: If ``True`` any running acquisition will be stopped. If ``False`` and an acquisition is
            already running, an error will be raised.

        Returns:
            True if arming was successful else False
        """
        with self._acquisition_lock:  # Acquire lock to prevent concurrent exposures
            if self._acquisition_thread is not None:
                if kill_running:
                    self.stop()
                else:
                    log.error("Acquisition already in progress")
                    return False
            if metadata is not None:
                self.update_payload_metadata(metadata)
            if self._arm():
                # emit event
                self.acquisition_started(self.get_configuration())
                return True
            return False

    # events which emitted by each device
    @event
    def acquisition_data(self, frame: np.ndarray, metadata: dict | None = None) -> tuple:
        """
        Event to emit new frames.

        .. note::
            The dtype of the frame is not changed here.

        Args:
            frame: The frame payload data (for example an image or an scope trace)
            metadata: The metadata which is passed along the payload. This argument takes precedence over the
                :code:`payload_metadata` attribute (for example set by the :code:`update_payload_metadata` method)
                while merging the two dicts.

        Returns:
            A tuple of image and metadata(-dict)
        """
        if metadata is None:
            metadata = {}
            log.info(f"Emitting frame without metadata with shape {frame.shape} and dtype {frame.dtype}")
        else:
            log.info(f"Emitting frame {metadata['frame']} with shape {frame.shape} and dtype {frame.dtype}")
        metadata = self.payload_metadata | metadata
        return frame, metadata

    @event
    def acquisition_started(self, metadata: dict | None = None) -> dict:
        """
        Event emitted when the acquisition thread starts.

        Returns:
            A dict with acquisition metadata
        """
        self.acquisition_running = True
        if metadata is None:
            return {}
        return metadata

    @event
    def acquisition_stopped(self, metadata: dict | None = None) -> dict:
        """
        Event emitted when the acquisition thread stops.

        Returns:
            A dict with acquisition metadata
        """
        self.acquisition_running = False
        if metadata is None:
            return {}
        return metadata

    # the following methods need to be implement for specific devices
    @abstractmethod
    def _open(self) -> Any:
        """
        Device specific code to open the device handler and return it.

        .. code-block:: python

            # open camera via vendor API
            camera = vencor_api.get_handle()
            camera.connect()
            return camera
        """

    @abstractmethod
    def _teardown(self) -> None:
        """
        Device specific code to release the device handler and potentially de-initialize the API.

        .. code-block:: python

            # close camera
            with self.get_device() as camera:
                camera.disconnect()
            vendor_api.close()
        """

    @abstractmethod
    def _start(self) -> bool:
        """
        Device specific code to fire a software trigger.

        .. code-block:: python

            # trigger camera via API
            with self.get_device() as camera:
                camera.trigger_now()
            return True

        Returns:
            True if successful
        """

    @abstractmethod
    def _stop(self) -> bool:
        """
        Device specific code to abort the exposure and release queued buffers.

        .. attention::

            Stop any running acquisition threads here. To signal a potention thread,
            you can use :attr:`_stop_acquisition_event`.

        .. code-block:: python

            # abort exposure
            with self.get_device() as camera:
                camera.abort_exposure()
                camera.buffers.release()

        Returns:
            True if successful
        """

    @abstractmethod
    def _get_status(self) -> dict:
        """
        Device specific code to get a dict with the current device status.

        .. code-block:: python

            # get sensor temp
            with self.get_device() as camera:
                temp = camera.get_prop("sensor_temp")
            return {"sensor_temp": temp}

        Returns:
            A dict with the device status
        """

    @abstractmethod
    def _set_config(self, config: dict) -> bool:
        """
        Device specific code to configure device features.

        .. code-block:: python

            # apply config
            for key, val in config:
                try:
                    with self.get_device() as camera:
                        camera.apply_prop(name=key, value=val)
                except Exception as e:
                    log.error(e)
                    return False
            return True

        Args:
            config: A valid configuration dict passed from :meth:`set_config`

        Returns:
            True if configuration is possible
        """

    @abstractmethod
    def _arm(self) -> bool:
        """
        Device specific code to arm the device with the currently active configuration.

        .. code-block:: python

            # arm exposure
            try:
                with self.get_device() as camera:
                    camera.arm(frame_count = 4)
                self._start_acquisition_thread()  # has to be implement for the specific device
                return True
            except Exception as e:
                log.error(e)
                return False

        Returns:
            True if arming was successful else False
        """
