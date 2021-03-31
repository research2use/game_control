import sys


def is_linux():
    return sys.platform in ["linux", "linux2"]


def is_windows():
    return sys.platform == "win32"
