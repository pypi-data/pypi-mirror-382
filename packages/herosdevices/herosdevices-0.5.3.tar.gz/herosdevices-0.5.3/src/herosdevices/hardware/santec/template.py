"""Template for Santec SLMs."""

import numpy as np
import numpy.typing as npt


class SantecSLMTemplate:
    """Template for Santec SLMs.

    Has no functionality, use the derived classes instead.
    """

    def __init__(self) -> None:
        pass

    def firmware_serialnumber(self) -> str:
        """Get the serial number of the santec firmware running on the SLM.

        This not the same as the serial number used to identify the FTDI chip.

        Returns:
            Serial number.
        """
        raise NotImplementedError

    def video_mode(self, mode: int = 0) -> str:
        """
        Query or set the video source the SLM draws the images from.

        Args:
            mode: Video source. Consult the manual for for possible sources.
        """
        raise NotImplementedError

    def push_image(self, slot: int, image: npt.NDArray[np.uint16]) -> str:
        """
        Upload an image into a specified memory slot.

        Args:
            slot: Slot number. Slot numbers range from 1 to 128.
            image: The image.
        """
        raise NotImplementedError

    def contrast_level(self, value: int) -> str:
        """Set the contrast/gamma level of the LCOS."""
        raise NotImplementedError

    def display_slot(self, slot: int = 1) -> str:
        """Set the memory slot to display on the SLM.

        Args:
            slot: Slot number. The lowest slot number is 1.
        """
        raise NotImplementedError
