from pathlib import Path

import cv2
import numpy as np
import pytest

from game_control.frame import Frame
from game_control.sprite import Sprite


def test_discover_sprites():
    sprites_dir = Path(__file__).parent / "test_sprite_data"
    sprites = Sprite.discover_sprites(sprites_dir)
    expected_sprites = {
        "SPRITE_BLUE_RED": ((46, 69, 3), [(255, 0, 0), (0, 0, 255)]),
        "SPRITE_GREEN": ((39, 149, 3), [(0, 255, 0)]),
        "SPRITE_YELLOW": ((42, 196, 3), [(0, 255, 255)]),
    }

    assert len(expected_sprites) == len(sprites)
    for name, sprite in sprites.items():
        shape = sprite.image_data.shape
        expected_shape, expected_bgr_values = expected_sprites[name]
        expected_shape += (len(expected_bgr_values),)
        assert shape == expected_shape

        for i in range(shape[3]):
            img = sprite.image_data[..., i]
            expected_img = np.full(shape[0:3], expected_bgr_values[i], dtype=np.uint8)
            assert np.allclose(img, expected_img)


# (top, left, bottom, right) region of Brawl Stars button in full image
REGION = (103, 315, 185, 384)


@pytest.mark.parametrize("sprite_name", ["SPRITE_BUTTON1", "SPRITE_BUTTON2"])
@pytest.mark.parametrize("frame_filename", ["screen1.png", "screen2.png"])
@pytest.mark.parametrize("region", [REGION, None])
@pytest.mark.parametrize("use_global_location", [True, False])
def test_locate(sprite_name, frame_filename, region, use_global_location):
    # Read img; make Frame
    data_dir = Path(__file__).parent / "test_sprite_locator_data"
    img = cv2.imread(str(data_dir / "screenshots" / frame_filename))
    frame = Frame(img, None)

    # Read sprites; select one
    sprites = Sprite.discover_sprites(data_dir / "sprites")
    sprite = sprites[sprite_name]

    # Try to locate sprite in frame
    location = Sprite.locate(sprite, frame, region, use_global_location)

    # Generate expectation dynamically for parameterized combinations
    if sprite_name == "SPRITE_BUTTON1" and frame_filename == "screen1.png":
        if region and not use_global_location:
            expected_location = (0, 0, 82, 69)
        else:
            expected_location = REGION
    else:
        expected_location = None

    # Verify
    assert location == expected_location
