"""HERO driver and functions to control a Santec SLM."""

import logging
import struct
import sys
import time

import numpy as np
import numpy.typing as npt

from herosdevices.helper import log

from .template import SantecSLMTemplate

try:
    import ftd3xx

    if sys.platform == "win32":
        import ftd3xx._ftd3xx_win32 as _ft
    elif sys.platform.startswith("linux"):
        import ftd3xx._ftd3xx_linux as _ft
except ImportError as ex:
    msg = """Missing ftd3xx python module.
    Get it from:
        https://www.ftdichip.com/Support/SoftwareExamples/FT60X.htm
    and install it. Make sure to also install D3XX driver for your platform.
    Find it here:
        https://www.ftdichip.com/Drivers/D3XX.htm
    """
    raise ImportError(msg) from ex

WORD_LENGTH = 4
IMAGESIZE = (1200, 1920)

fpga_status = {
    "OK": "Command successful",
    "BS": "Boot in progress",
    "NG": "Error: Could not execute command",
    "NO RESPONSE": "No answer received from the FPGA (yet)",
}

video_mode = {"USB": 0, "DVI": 1}  # DVI Mode is not supported by the driver yet!

# FPGA request types
cmd_control = {"id": 1, "magic_length": 0xFF}
cmd_statusrequest = {"id": 2, "magic_length": 0}
cmd_statusresponse = {"id": 3, "magic_length": 0xFF}
cmd_imagedata = {"id": 4, "magic_length": 0x03BF}


def _checksum_image(image: npt.NDArray[int]) -> int:
    """Calculate checksum by interpreting an image as as sequence of UNSIGNED SHORTS (2 Byte) and summing over those.

    Note: for large images, this checksum can easily overrun the range of an int! But this is intended on the SLM200.

    Args:
        image: The image.

    Returns:
        The checksum.
    """
    return int(image.sum())


class SLM200(SantecSLMTemplate):
    """
    Driver for a Santec SLM200 spatial light modulator.

    The images can be transferred to the SLM200 via USB or DVI. This driver, however, only supports
    communication via USB. Since image upload via USB takes roughly 150ms, this driver is limited to
    around 6Hz of refresh rate. Precise and externally synchronized timing is only possible in USB mode.

    In USB mode (also called memory mode) images can be pushed via USB and stored in one of 128 memory
    slots. The image slot displayed on the SLM can be set randomly by the driver or an advance from one
    slot to the next can be triggered by a software trigger, and internal timer, or a logic signal
    (Trigger IN SMB jack).

    The SLM contains an FPGA that the computer communicates with by writing to an output FIFO/pipe
    and reading from an input FIFO/pipe. These two FIFOs are transparently accessed through the FTDI
    driver (D3xx) which provides methods to read and write these FIFOs/pipes.

    This driver is reverse engineered by looking at the data the vendor software sends via USB.
    This was achieved by looking at the API calls to the functions FT_WritePipe and FT_ReadPipe
    in the D3XX.dll which handles the communication with the FTDI USB3.0 chip (FT601).
    """

    firmware_versions = ["2018021001", "2018021101", "2018020001", "2017080002", "2015010001"]
    trigger_functions = {
        "none": {"start": None, "stop": None},
        "manual": {
            "start": lambda x: SLM200._trigger_software(x, True),
            "stop": lambda x: SLM200._trigger_software(x, False),
        },
        "external": {
            "start": lambda x: SLM200._trigger_external(x, True),
            "stop": lambda x: SLM200._trigger_external(x, False),
        },
        "auto": {"start": lambda x: SLM200._trigger_auto(x, True), "stop": lambda x: SLM200._trigger_auto(x, False)},
    }

    def __init__(
        self, serialnumber: str, channel: int = 0, streaming_mode: bool = False, request_sleep: float = 0.015
    ) -> None:
        self.serialnumber = serialnumber
        self.channel = channel
        self.bStreamingMode = streaming_mode
        self.request_sleep = request_sleep

        self.trigger_mode = "none"

        if sys.platform.startswith("linux"):
            self.endpoints = {"out": channel, "in": channel}
        else:
            self.endpoints = {"out": 2 + channel, "in": 130 + channel}

        devices = ftd3xx.listDevices(_ft.FT_OPEN_BY_SERIAL_NUMBER)
        try:
            idx = [dev.decode("utf-8") for dev in devices].index(self.serialnumber)
        except Exception as e:
            msg = f"Device with serial number {serialnumber} not found"
            raise RuntimeError(msg) from e
        self.d3xx = ftd3xx.create(devices[idx], _ft.FT_OPEN_BY_SERIAL_NUMBER)

        # set input pipe timeout to 1 second
        if sys.platform == "win32":
            self.d3xx.setPipeTimeout(self.endpoints["in"], 1000)

        # clear read pipe. To check no residual response is in the input pipe, we issue a SN command
        # and repeat until we receive a valid serial number.
        self.d3xx.flushPipe(self.endpoints["in"])
        for _ in range(10):
            firmware = self.firmware_serialnumber()
            if firmware not in self.firmware_versions:
                self.status()
            else:
                self.firmware = firmware
                break

    def _command_assemble(self, cmd_dict: dict, payload: bytes, seq_id: int = 0) -> bytes:
        if cmd_dict["magic_length"] == 0xFF:  # noqa:PLR2004
            padded_payload = bytearray(1024)
            padded_payload[: len(payload)] = payload
            payload = padded_payload
        return struct.pack(">4sHxBIxxxx", b"SEND", cmd_dict["magic_length"], cmd_dict["id"], seq_id) + payload

    def _command_disassemble(self, buffer: bytes) -> dict:
        _, magic_length, idx = struct.unpack(">4sHxBxxxxxxxx", buffer[0:16])
        return {"magic_length": magic_length, "id": idx, "payload": buffer[16:]}

    def write_command(self, cmd_dict: dict, payload: bytes, seq_id: int = 0) -> None:
        """Send a command to the SLM."""  # TODO: what are arguments doing?
        self.write(self._command_assemble(cmd_dict, payload, seq_id))

    def read_command(self, length: int) -> dict:
        """Read a command response from the SLM.

        Args:
            length: Length of the response to read in byte.
        """
        return self._command_disassemble(self.read(length))

    def status(self) -> str:
        """Get the current status of the SLM.

        Returns:
            Status string.
        """
        self.write_command(cmd_statusrequest, b"")
        res = self.read_command(16 + 1024)
        if res["id"] != 3 and res["magic_length"] != 255:  # noqa: PLR2004
            msg = f"Invalid status response: {res}"
            raise RuntimeError(msg)
        return res["payload"].decode("utf-8").split("\x00")[0].strip()

    def request(
        self,
        cmd_dict: dict,
        payload: bytes,  # TODO: make this also optional
        buffer: bytes | None = None,
        trials: int = 100,
        request_sleep: float | None = None,
    ) -> str:
        """Send a request to the SLM and wait for a response.

        Args:
            cmd_dict: Dictionary containing command metadata.
            payload: Payload to send. Unused when buffer is used
            buffer: Pre-assembled buffer to send.
            trials: Number of trials to attempt.
            request_sleep: Sleep time between retries.

        Returns:
            Status string.
        """
        if request_sleep is None:
            request_sleep = self.request_sleep
        if buffer is None:
            self.write_command(cmd_dict, payload)
        else:
            self.write(buffer)
        for _ in range(trials):
            status = self.status()
            if status != "NO RESPONSE":
                break
            time.sleep(request_sleep)
        # check if system is booting. If it is, wait 1s and try again
        if status in ("BS", "TO"):
            log.warning("The SLM is booting. Waiting for 1s and try again!")
            time.sleep(1)
            status = self.request(cmd_dict, payload, buffer, trials, request_sleep)
        return status

    def write(self, buffer: bytes) -> None:
        """Stream buffered data to the SLM."""
        # enable streaming mode
        if self.bStreamingMode and sys.platform.startswith("linux"):
            self.d3xx.setStreamPipe(self.endpoints["out"], len(buffer))
            self.d3xx.setStreamPipe(self.endpoints["in"], len(buffer))

        bytes_written = self.d3xx.writePipe(self.endpoints["out"], buffer, len(buffer))
        assert bytes_written == len(buffer)
        log.debug("OUT(%i) %s", self.endpoints["out"], buffer)

        # disable streaming mode
        if self.bStreamingMode and sys.platform.startswith("linux"):
            self.d3xx.clearStreamPipe(self.endpoints["out"])
            self.d3xx.clearStreamPipe(self.endpoints["in"])

    def read(self, length: int) -> bytes:
        """Read `length` bytes from the device."""
        bytes_read = 0
        buffer_read = b""
        while bytes_read < length:
            output = self.d3xx.readPipeEx(self.endpoints["in"], length - bytes_read, raw=True)
            bytes_read += output["bytesTransferred"]
            buffer_read += output["bytes"].decode("latin1")
        log.debug("IN(%i) %s", self.endpoints["in"], buffer_read)
        return buffer_read

    def _controlcommand(self, command: bytes, param_list: list[int] | None = None, longrunning: bool = False) -> str:
        """
        Call a get or set function on the SLM depending on whether parameter param is given.

        Args:
            command: Two character command identifier for control commands.
            param_list: Parameters to set. empty, if a read command should be issued.
            longrunning: Flag if the command runs for a long(er) time.
        """
        payload = command
        if param_list is not None:
            for param in param_list:
                payload += b" %i" % (param)
        payload += b"\x0d"
        return self.request(cmd_control, payload, request_sleep=1 if longrunning else self.request_sleep)

    def firmware_serialnumber(self) -> str:
        """Get the serial number of the santec firmware running on the SLM.

        This not the same as the serial number used to identify the FTDI chip.

        Returns:
            Serial number.
        """
        return self._controlcommand(b"SN")

    def video_mode(self, mode: int = 0) -> str:
        """
        Query or set the video source the SLM draws the images from.

        Args:
            mode: Video source. 0 = USB/Memory, 1 = DVI.

        Returns:
            Status of the operation.
        """
        return self._controlcommand(b"VI", [mode])

    def _upload_slot(self, slot: int) -> str:
        """
        Set the memory slot to upload the next image to.

        Args:
            slot: Slot number. The lowest slot number is 1.

        Returns:
            Status of the operation.
        """
        return self._controlcommand(b"MI", [slot])

    def display_slot(self, slot: int = 1) -> str:
        """Set the memory slot to display on the SLM.

        Args:
            slot: Slot number. The lowest slot number is 1.

        Returns:
            Status of the operation.
        """
        return self._controlcommand(b"DS", [slot])

    def contrast_level(self, value: int) -> str:
        """
        Set the contrast/gamma level of the LCOS.

        Args:
            value: Value between 0 and 1023.

        Returns:
            Status of the operation.
        """
        return self._controlcommand(b"GS", [value])

    def trigger_output(self, on: bool | None = None) -> str:
        """Activate the trigger output of the SLM.

        This is especially useful in DVI mode orwhen software/automatic triggers are used.

        Args:
            on: Determines whether the trigger output should be activated.
                If not set the current status is returned.

        Returns:
            tatus of the operation.
        """
        if on is None:
            return self._controlcommand(b"TM")
        return self._controlcommand(b"TM", [1 if on else 0])

    def _trigger_external(self, on: bool = True) -> str:
        """
        Set SLM to react on external trigger.

        Args:
            on: Determines whether the hardware trigger input should be used.

        Returns:
            Status of the operation.
        """
        return self._controlcommand(b"TI", [1 if on else 0])

    def _trigger_auto(self, on: bool = True, period: float = 2) -> str:
        """
        Set SLM to trigger periodically.

        Args:
            on: Determines whether the auto trigger should be used.
            period: Trigger period time in s. Can range from 1/60 to 2.

        Returns:
            Status of the operation.
        """
        if on:
            self._controlcommand(b"MW", [int(period * 60)])
            self._controlcommand(b"DR", [1])
        else:
            self._controlcommand(b"DB")
            self._controlcommand(b"MP", [1])
            self._controlcommand(b"MW", [0])

    def _trigger_software(self, on: bool) -> str:
        """
        Set SLM to react on software trigger.

        Args:
            on: Determines whether the software trigger should be used.

        Returns:
            Status of the operation.
        """
        self._controlcommand(b"TC", [1])
        if on:
            self.trigger_software_fire()

    def trigger_software_fire(self) -> str:
        """Fire a software trigger. Only works if the trigger mode was set to manual before.

        Returns:
            Status of the operation.
        """
        if self.trigger_mode == "manual":
            return self._controlcommand(b"TS")
        return "FAILED"

    def trigger(self, mode: str | None = None) -> str:
        """Set or query the trigger mode.

        .. hint::
            The SLM can be triggered from four different sources:
                * none     : The image selected by :func:`display_slot` is displayed continuously \
                             and no trigger changes this.
                * manual   : The image in the next slot is displayed when the software trigger \
                             :func:`trigger_software_fire` is called.
                * auto     : The change to the next image is periodically triggered by an internal timer.
                * external : The change to the next image happens when a logic pulse on the trigger in \
                             SMB-connector is received.

        Args:
            mode: Name of the trigger mode to set. If no argument is given,
                  the current trigger mode is returned.

        Returns:
            The trigger mode.
        """
        if mode is None:
            return self.trigger_mode
        if mode in self.trigger_functions:
            if self.trigger_mode != "none":
                self.trigger_functions[self.trigger_mode]["stop"](self)
            if mode != "none":
                self.trigger_functions[mode]["start"](self)
            self.trigger_mode = mode
            return self.trigger_mode
        msg = f"Unknown trigger mode: {mode}"
        raise ValueError(msg)

    def phase_calibration(self, wavelength: int, max_phase: int = 2) -> str:
        """Calibrate the change of the lights phase as function of the bit value of each pixel.

        This can be used to adapt for different wavelength of the light and to change the
        maximum phase change for the maximum pixel value of 1023 (10bit).

        .. attention::
            This command takes some minutes to finish!

        Args:
            wavelength: Wavelength of the indicent light in nm.
            max_phase: Maximum phase change in units of pi.

        Returns:
            Status of the operation.
        """
        return self._controlcommand(b"WL", [wavelength, max_phase], longrunning=True)

    def push_image(self, slot: int, image: npt.NDArray[np.uint16]) -> str:
        """
        Upload an image into a specified memory slot.

        Args:
            slot: Slot number. Slot numbers range from 1 to 128.
            image: The image. Dimension must be (1200, 1920). Dtype must be 'u2' (`unit16`),
                   otherwise is it casted to 'u2' which might have unpredictable results.

        Returns:
            Status of the operation
        """
        if self._upload_slot(slot) != "OK":
            pass
            # raise Exception("Could not select image slot %i"%(slot)) #noqa: ERA001 TODO: is this needed?
        if image.shape != IMAGESIZE:
            msg = f"Image size {image.shape} is not correct. Must be {IMAGESIZE}"
            raise ValueError(msg)
        image = image.astype("u2")
        buffer = bytearray()
        for i, line in enumerate(image):
            linedata = bytearray(4096)
            linedata[: 2 * len(line)] = line.tobytes()
            buffer += self._command_assemble(cmd_imagedata, linedata, i)

        # set last four bytes of the buffer as uint32 checksum
        buffer[-4:] = struct.pack("I", _checksum_image(image) % 2**32)
        return self.request(None, None, buffer=bytes(buffer))

    def __del__(self) -> None:
        """Close connection and library."""
        self.d3xx.close()


if __name__ == "__main__":
    import numpy as np

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    serialnumber = "000000000001"
    slm = SLM200(serialnumber)

    # define test images
    testimage_offset = np.ones(IMAGESIZE, dtype=np.dtype("u2")) * 1023

    testimage_box = np.zeros(IMAGESIZE, dtype=np.dtype("u2"))
    testimage_box[300:900, 300:900] = 1023

    testimage_sine = np.zeros(IMAGESIZE, dtype=np.dtype("u2"))
    testimage_sine[:, :] = 1023 * np.sin(2 * np.pi * np.repeat([IMAGESIZE[1]], IMAGESIZE[0], axis=0) / 10) ** 2

    # Get serial number
    logger.info("Serial number: %s", slm.firmware_serial_number())
    logger.info("Change video mode to USB: %s", slm.video_mode(video_mode["USB"]))

    logger.info("Set gamma to 0: %s", slm.contrast_level(0))

    start_time = time.time()
    logger.info("Upload image to slot 1: %s", slm.push_image(1, testimage_box))
    logger.info("Upload image to slot 2: %s", slm.push_image(2, testimage_box[:, ::-1]))
    logger.info("Uploading took %.1f ms", (time.time() - start_time) * 1e3)

    # Display image uploaded to slot 1
    logger.info("Display slot 1: %s", slm.display_slot(1))

    # test software trigger
    slm.trigger("manual")
    for _ in range(10):
        time.sleep(1)
        slm.trigger_software_fire()

    # test automatic trigger (timer based)
    slm.trigger("auto")
    time.sleep(10)

    # set trigger to external an leave it like that
    slm.trigger("external")

    # query trigger mode
    logger.info("Trigger mode: %s", slm.trigger())
