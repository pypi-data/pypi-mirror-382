"""Driver for cameras based on the ids peak library."""

import os
import threading
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from types import ModuleType

from heros.helper import log

from herosdevices.core.templates.camera import CameraTemplate

try:
    from ids_peak import (
        ids_peak,  # type: ignore
        ids_peak_ipl_extension,  # type: ignore
    )
except ModuleNotFoundError:
    ids_peak = cast("ModuleType", None)
    ids_peak_ipl_extension = cast("ModuleType", None)
    log.exception("Could not import the 'ids_peak' or 'ids_peak_ipl' python module, required for using ids cameras")

DEFAULT_CONFIG = {
    "frame_count": -1,
    "timeout": -1,
}


class PeakCompatibleCamera(CameraTemplate):
    """
    A class to interface with IDS Peak cameras.

    The class provides functionality to control and capture images from IDS Peak cameras.
    It manages camera configuration, acquisition, and data streaming.

    Note:
        To access the camera as non-root user, you need to add the following udev rule
        to :code:`/etc/udev/rules.d/99-ids.rules`::

            ATTRS{idVendor}=="1409", MODE="666"

        The vendor library must be obtained from the [official website](https://en.ids-imaging.com/download-peak.html).
        Download the `IDS peak archive file`, unpack it at move the content of `idspeak/ids/cti/` to a place where
        the user running the driver can access it. This path then needs to be specified via the `lib_path` argument
        (see example below)

    Note:
        The :code:`node_map` attribute provides access to the camera node map. If you need to set some special
        nodes you can use that.
        You can find the available nodes in the official API manuals:

        - https://en.ids-imaging.com/manuals/ids-peak/ids-peak-api-documentation/2.16.0/en/index.html
        - https://en.ids-imaging.com/manuals/ids-peak/ids-peak-user-manual/1.3.0/en/preface.html

    Example:
        The class can be started with BOSS with the following example JSON dict::

            {
              "_id": "my_camera",
              "classname": "herosdevices.hardware.ids.PeakCompatibleCamera",
              "arguments": {
                "cam_id": "1410d4e7c3b5",
                "lib_path": "/opt/idspeak/ids/cti/",
                "default_config": "default",
                "config_dict": {
                  "default": {
                    "ExposureTime": 1000,
                    "TriggerSelector": "ExposureStart",
                    "TriggerMode": "On",
                    "TriggerSource": "Software",
                    "frame_count": 5,
                  }
                }
              }
            }


        The keys in the config dictionary starting with a capital letter are nodes in the camera node map.

    """

    _special_config_keys = ["frame_count", "timeout"]  # non peak node map config keys
    _datastream: ids_peak.DataStream
    node_map: ids_peak.NodeMap | None = None

    def __init__(
        self, cam_id: str, config_dict: dict, default_config: str | None = None, lib_path: str | None = None
    ) -> None:
        """Create a class to interface with IDS Peak cameras.

        Args:
            cam_id: Serial number of the cam. Can be obtained for example from the ids-peak GUI. Note, that the id
                is only the first part of the value shown in the GUI, the part including the device type is not
                unique and may not be added to :code:`cam_id`.
            lib_path: Path to vendor library.
            config_dict: Dict of configuration values like shown in the json example above.
            default_config: Default key in :code:`config_dict` to use.

        """
        self.cam_id = cam_id
        self.default_config_dict = DEFAULT_CONFIG
        if lib_path is not None:
            os.environ["GENICAM_GENTL32_PATH"] = lib_path
            os.environ["GENICAM_GENTL64_PATH"] = lib_path
        ids_peak.Library.Initialize()
        super().__init__(config_dict, default_config)

    def get_config_nodes(self, only_implemented: bool = True) -> dict:
        """Get all nodes from the camera in form of a dict including information about if they can be set/read.

        Args:
            only_implemented: Shows only nodes that are implemented on the attached camera. If False, returns
                all nodes the driver library knows
        """
        node_dict = {}
        with self.get_camera():
            for n in self.node_map.Nodes():  # type: ignore
                if not isinstance(n, ids_peak.CategoryNode):
                    node_props = {}
                    node_props["Display Name"] = n.DisplayName()
                    node_props["ToolTip"] = n.ToolTip()
                    node_props["IsReadable"] = n.IsReadable()
                    node_props["IsWriteable"] = n.IsWriteable()
                    if not only_implemented or n.IsImplemented():
                        node_dict[n.Name()] = node_props
        return node_dict

    def _open(self) -> ids_peak.Device:
        """Open the connection to the device. Don't call directly.

        :meta private:
        """
        device_manager = ids_peak.DeviceManager.Instance()
        device_manager.Update()
        for i, device in enumerate(device_manager.Devices()):
            if self.cam_id in device.ID():
                camera = device_manager.Devices()[i].OpenDevice(ids_peak.DeviceAccessType_Control)
                break
        else:
            msg = f"Camera {self.cam_id} not found."
            raise RuntimeError(msg)

        self.node_map = camera.RemoteDevice().NodeMaps()[0]
        return camera

    def _set_config(self, config: dict) -> bool:
        with self.get_camera():
            for key, value in config.items():
                if key not in self._special_config_keys:
                    node = self.node_map.FindNode(key)  # type: ignore
                    if type(node) is ids_peak.FloatNode:
                        node.SetValue(value)
                    elif type(node) is ids_peak.EnumerationNode:
                        node.SetCurrentEntry(value)
                    else:
                        msg = f"Unrecognised node type: {type(node)}"
                        raise ValueError(msg)
        return True

    def _acquisition_loop(self) -> None:
        meta_data = {}
        frame_id = 0
        config = self.get_configuration()
        frame_count = config["frame_count"]
        if config["timeout"] == -1:
            timeout = ids_peak.Timeout.Timeout(config["timeout"] * 1e3)
        else:
            timeout = ids_peak.Timeout.INFINITE_TIMEOUT

        while not self._stop_acquisition_event.is_set() and (frame_id < frame_count - 1 or frame_count < 0):
            try:
                buffer = self._datastream.WaitForFinishedBuffer(timeout)
                if buffer.DeliveredDataSize() > 0:
                    frame_id = buffer.FrameID()
                    meta_data["frame"] = frame_id
                    meta_data["acquisition_time"] = buffer.Timestamp_ns()
                    ipl_image = ids_peak_ipl_extension.BufferToImage(buffer)
                    self._datastream.QueueBuffer(buffer)
                    img_array = ipl_image.get_numpy_2D().copy()
                    self.acquisition_data(img_array, meta_data)
            except ids_peak.AbortedException:
                self._stop_acquisition_event.set()

        if frame_count > 0:
            if frame_id != frame_count - 1:
                log.error("Incorrect number of received frames: %s  instead of %s!", frame_id, frame_count)
        self.stop()

    def _arm(self) -> bool:
        with self.get_camera() as camera:
            self.node_map.FindNode("TLParamsLocked").SetValue(1)  # type: ignore
            try:
                self._datastream = camera.DataStreams()[0].OpenDataStream()
            except ids_peak.BadAccessException:
                self._datastream = camera.DataStreams()[0].OpenedDataStream()
                self._datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)
                for buffer in self._datastream.AnnouncedBuffers():
                    self._datastream.RevokeBuffer(buffer)
            payload_size = self.node_map.FindNode("PayloadSize").Value()  # type: ignore
            max_buffer = self._datastream.NumBuffersAnnouncedMinRequired() * 5
            for _ in range(max_buffer):
                buffer = self._datastream.AllocAndAnnounceBuffer(payload_size)
                self._datastream.QueueBuffer(buffer)
            self._datastream.StartAcquisition()
            self.node_map.FindNode("AcquisitionStart").Execute()  # type: ignore
            self.node_map.FindNode("AcquisitionStart").WaitUntilDone()  # type: ignore

            self._start_acquisition_thread()
        return True

    def _start_acquisition_thread(self) -> None:
        """Start the acquisition thread."""
        log.debug("Starting acquisition thread")
        self._stop_acquisition_event.clear()
        self._acquisition_thread = threading.Thread(target=self._acquisition_loop)
        self._acquisition_thread.start()

    def _start(self) -> bool:
        self.node_map.FindNode("TriggerSoftware").Execute()  # type: ignore
        return True

    def _stop(self) -> bool:
        if self.acquisition_running is False or self._acquisition_thread is None:
            self.acquisition_running = False
            return True
        try:
            self.node_map.FindNode("AcquisitionStop").Execute()  # type: ignore

            if threading.current_thread().ident != self._acquisition_thread.ident:
                # Kill the datastream to exit out of pending `WaitForFinishedBuffer` calls
                self._datastream.KillWait()
                self._acquisition_thread.join()
                self.acquisition_stopped()
            else:
                # only set stop flag if closed from acquisition thread itself
                self._datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)

            # Unlock parameters
            self.node_map.FindNode("TLParamsLocked").SetValue(0)  # type: ignore
            self._acquisition_thread = None
        except Exception as e:  # noqa: BLE001
            log.error("Exception (stop acquisition): %s", str(e))
            return False
        else:
            return True

    def _get_status(self) -> dict:
        return {
            "acquisition_running": self.acquisition_running,
        }

    def _teardown(self) -> None:
        log.debug(f"closing down connection to {self.cam_id}")
        self.stop()
        self.node_map = None
        self._device = None

    def __del__(self) -> None:
        """Call teardown method and close ids_peak library on delete."""
        self.teardown()
        ids_peak.Library.Close()
