import sys


def is_linux():
    return sys.platform in ["linux", "linux2"]


def is_windows():
    return sys.platform == "win32"


def extract_roi_from_image(image, region_bounding_box):
    return image[
        region_bounding_box[0] : region_bounding_box[2],
        region_bounding_box[1] : region_bounding_box[3],
    ]
