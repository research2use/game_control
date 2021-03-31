import time
from abc import ABC, abstractmethod

from game_control.frame_grabber import FrameGrabber
from game_control.input_controller import InputController
from game_control.window_controller import WindowController

"""
Note that Windows zoom/scaling is not yet taken into account correctly,
so for now make sure that the scale factor is set to 100%
(On Win10: 'Change the size of apps and text on the main display')
"""


class Game(ABC):
    """Abstract base class to control a game.

    Consists mainly of the following components:
        * a window controller to position, resize, focus etc. the game window
        * an input controller to send key and mouse commands to the game
        * a frame grab to take screen shots of the gam

    Derived classes need to implement the start() and stop() methods that
    respectively start and stop a game.
    At least two ready to use derived classes are defined in the games subfolder:
        * one for starting a game via an executable
        * and one for starting a game in a web browser via an url

    """

    def __init__(
        self,
        top=0,
        left=0,
        width=960,
        height=540,
        window_name=None,
        wait_for_focus=5,
        **kwargs,
    ):
        """Constructs a game, starts it and initializes the window.

        Args:
            left (int): Initial window position: number of pixel from the left.
            top (int): Initial window position: number of pixels from the top.
            width (int): Initial window position: width of window in pixels.
            height (int): Initial window position : height of window in pixels.
            window_name (str): Give name of the game window if you know it for
                fast initialization. Set to None to use the window with focus.
            wait_for_focus (int): Seconds to wait for game to start and get
                focus when window_name is not given.
            **kwargs: Extra args for implementation of abstract method start().

        """
        self._initial_window_region = {
            "top": top,
            "left": left,
            "width": width,
            "height": height,
        }
        self._frame_grabber = FrameGrabber()
        self._window_controller = WindowController()
        self._input_controller = InputController(game=self)
        self.start(**kwargs)
        if window_name:
            self._window_name = window_name
        else:
            print(f"Waiting {wait_for_focus} seconds for game to start and get focus")
            time.sleep(wait_for_focus)
            self._window_name = self._window_controller.get_focused_window_name()
        print("Window name of game =", self._window_name)
        self._window_id = self._initialize_window()

    @abstractmethod
    def start(self):
        """Starts the game and makes sure it has focus afterwards.

        Abstract method that needs to be implemented in derived class.

        """
        pass

    @abstractmethod
    def stop(self):
        """Stops the game.

        Abstract method that needs to be implemented in derived class.

        """
        pass

    @property
    def input_controller(self):
        """InputController: object to send keyboard and mouse commands to the game."""
        return self._input_controller

    def _get_window_id(self):
        """Tries to fetch id of the window from its name.

        Returns:
            int/None: Id of the window if it can be fetched; None otherwise.
        """
        window_id = self._window_controller.locate_window(self._window_name)
        return None if window_id in [0, "0"] else window_id

    def _initialize_window(self):
        """Tries to focus the game window and move/resize it to its intial position.

        Returns:
            int: Id of the window if it can be fetched; None otherwise.

        Raises:
            RuntimeError: when window could not be found.
        """
        max_attempts = 100
        window_id = None
        for _ in range(max_attempts):
            window_id = self._get_window_id()
            if window_id:
                break
            time.sleep(0.1)
        time.sleep(3)

        if not window_id:
            raise RuntimeError("Could not find window...")

        self._window_controller.move_window(window_id, 0, 0)
        self._window_controller.focus_window(window_id)
        self._window_controller.set_window_geometry(
            window_id, self._initial_window_region
        )

        return window_id

    def is_launched(self):
        """bool: True when game was launched succesully; False otherwise."""
        return self._get_window_id() is not None

    def is_focused(self):
        """bool: True when game window has focus; False otherwise."""
        return self._window_controller.is_window_focused(self._window_id)

    def grab_frame(self):
        """Make screenshot of the game window, but only when it has focus.

        Returns:
            Frame/None: grabbed frame when window has focus; None otherwise.
                img in frame is an ndarray with 3 dimensions:
                2D grid with 3 channel uint8 BGR info per pixel
        """
        frame = None
        if self.is_focused():
            region = self._window_controller.get_window_geometry(self._window_id)
            frame = self._frame_grabber.grab_frame(region)
        return frame
