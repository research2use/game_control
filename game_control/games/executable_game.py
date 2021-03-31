import shlex
import subprocess

from game_control.game import Game


class ExecutableGame(Game):
    """Implementation of abstract base class to control an executable game."""

    def __init__(self, executable_filepath, **kwargs):
        """Constructs and starts an executable game.

        Args:
            executable_filepath (str): filepath of the executable of the game

        """
        self._executable_filepath = executable_filepath
        super().__init__(**kwargs)

    def start(self):
        """Starts the game executable in a separate process."""
        self._process = subprocess.Popen(shlex.split(self._executable_filepath))

    def stop(self):
        """Stops the game by terminating the process."""
        self._process.terminate()
