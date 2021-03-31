from game_control.utilities import is_linux, is_windows
import time

class WindowControllerError(BaseException):
    pass


class WindowController:

    def __init__(self):
        self.adapter = self._load_adapter()()

    def locate_window(self, name):
        return self.adapter.locate_window(name)

    def move_window(self, window_id, x, y):
        self.adapter.move_window(window_id, x, y)

    def resize_window(self, window_id, width, height):
        self.adapter.resize_window(window_id, width, height)

    def focus_window(self, window_id):
        self.adapter.focus_window(window_id)

    def bring_window_to_top(self, window_id):
        self.adapter.bring_window_to_top(window_id)

    def is_window_focused(self, window_id):
        return self.adapter.is_window_focused(window_id)

    def get_focused_window_name(self):
        return self.adapter.get_focused_window_name()

    def get_window_geometry(self, window_id):
        return self.adapter.get_window_geometry(window_id)

    def set_window_geometry(self, window_id, region):
        self.adapter.move_window(window_id, region["left"], region["top"])
        self.adapter.resize_window(window_id, region["width"], region["height"])

    def _load_adapter(self):
        if is_linux():
            from game_control.window_controllers.linux_window_controller import LinuxWindowController
            return LinuxWindowController
        elif is_windows():
            from game_control.window_controllers.win32_window_controller import Win32WindowController
            return Win32WindowController
