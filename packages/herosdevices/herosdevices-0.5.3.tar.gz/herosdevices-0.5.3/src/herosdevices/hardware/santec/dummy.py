"""Dummy SLM for testing purposes."""

import logging

import numpy as np
import numpy.typing as npt

from .template import SantecSLMTemplate

log = logging.getLogger("dummy slm")
log.setLevel("INFO")


class SantecDummySLM(SantecSLMTemplate):
    """Dummy SLM for testing purposes."""

    def __init__(self, slots: int = 32) -> None:
        self.images = [None] * slots

    def firmware_serialnumber(self) -> str:
        """Return a dummy firmware serial number."""
        return "20090123_142415"

    def video_mode(self, mode: int = 0) -> str:
        """Return always 'OK'. Dummy function."""
        del mode
        return "OK"

    def push_image(self, slot: int, image: npt.NDArray[np.uint16]) -> str:
        """Push image data into the dummy slot and return ok."""
        if slot < len(self.images):
            self.images[slot] = image
        return "OK"

    def contrast_level(self, value: int) -> str:
        """Return always 'OK'. Dummy function."""
        del value
        return "OK"

    def display_slot(self, slot: int = 1) -> str:
        """Return always 'OK'. Dummy function."""
        log.info("displaying image in slot %s", slot)
        return "OK"
