from datetime import datetime

import mss
import numpy as np

from game_control.frame import Frame
from game_control.frame_buffer import FrameBuffer


class FrameGrabber:
    """Frame grabber to make screenshots of a game."""

    def __init__(self, fps=2, buffer_seconds=2):
        maxlen = buffer_seconds * fps
        self._frame_buffer = FrameBuffer(maxlen=maxlen)
        self._screen_grabber = mss.mss()

    @property
    def frame_buffer(self):
        return self._frame_buffer

    def grab_frame(self, region):
        """Make screenshot of given subregion of the screen.

        Args:
            region (dict): region of screen you want to capture:
                {
                    "top": number of pixels from top (y coordinate),
                    "left": number of pixels from left (x coordinate),
                    "width": width of region,
                    "height": height of region,
                }
        Returns:
            Frame: containing ndarray with 3 dimensions
                (2D grid with 3 channel uint8 BGR info per pixel)
                and current datetime of capture

        """
        frame = np.array(self._screen_grabber.grab(region))

        frame = Frame(frame[..., :3], timestamp=datetime.now())
        self.frame_buffer.add_frame(frame)

        return frame
