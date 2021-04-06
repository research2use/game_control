import random
import time
from datetime import datetime


class Limiter:
    """Can be used to slow down processing"""

    def __init__(self, fps=2):
        """Construct limiter

        Args:
            fps (number/tuple): Requested number of processing steps per second.
                Will pause between start() and stop_and_delay() to reach fps.
                Requested fps can be an int or a tuple (indicating a random
                range to choose from).
        """
        self._fps = fps
        self._started_at = None

    def start(self):
        """Start the limiter"""
        self._started_at = datetime.utcnow()

    def _requested_duration(self):
        """Requested duration of a step between start and stop_and_delay

        Returns:
            float: duration in seconds based on requested fps
        """
        if isinstance(self._fps, (float, int)):
            fps = self._fps
        else:
            fps = random.uniform(self._fps[0], self._fps[1])
        return 1 / fps

    def stop_and_delay(self):
        """Stop the limiter and pause when necessary to reach requested fps

        Returns:
            (tuple): three floats representing respectively
                Requested duration to be between start and stop_and_delay
                Actual duration between start and stop_and_delay.
                Duration that was paused.
        """
        requested_duration = self._requested_duration()

        duration = (datetime.utcnow() - self._started_at).microseconds / 1000000
        remaining_duration = requested_duration - duration
        paused_duration = max(remaining_duration, 0)
        time.sleep(paused_duration)

        return requested_duration, duration, paused_duration
