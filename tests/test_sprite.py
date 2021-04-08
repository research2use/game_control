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


def _locate_helper(sprite_name, frame_filename, region, use_global_location):
    data_dir = Path(__file__).parent / "test_sprite_locator_data"
    img = cv2.imread(str(data_dir / "screenshots" / frame_filename))
    frame = Frame(img, None)
    sprites = Sprite.discover_sprites(data_dir / "sprites")
    sprite = sprites[sprite_name]
    location = Sprite.locate_template(sprite, frame, region, use_global_location)
    return location


# (top, left, bottom, right) region of Brawl Stars button in full image
APP_REGION = (103, 315, 185, 384)
BRAWLERS_REGION = (301, 28, 337, 92)
TRY_REGION = (485, 44, 523, 234)


@pytest.mark.parametrize(
    "sprite_name, frame_filename, region, use_global_location, expected_location",
    [
        # SPRITE_APP visible in ldplayer.png (but not all regions)
        ("SPRITE_APP", "ldplayer.png", APP_REGION, False, (0, 0, 82, 69)),
        ("SPRITE_APP", "ldplayer.png", APP_REGION, True, APP_REGION),
        ("SPRITE_APP", "ldplayer.png", BRAWLERS_REGION, False, None),
        ("SPRITE_APP", "ldplayer.png", BRAWLERS_REGION, True, None),
        ("SPRITE_APP", "ldplayer.png", TRY_REGION, False, None),
        ("SPRITE_APP", "ldplayer.png", TRY_REGION, True, None),
        ("SPRITE_APP", "ldplayer.png", None, False, APP_REGION),
        ("SPRITE_APP", "ldplayer.png", None, True, APP_REGION),
        # SPRITE_BRAWLERS visible in brawlstars.png (but not all regions)
        ("SPRITE_BRAWLERS", "brawlstars.png", APP_REGION, False, None),
        ("SPRITE_BRAWLERS", "brawlstars.png", APP_REGION, True, None),
        ("SPRITE_BRAWLERS", "brawlstars.png", BRAWLERS_REGION, False, (0, 0, 36, 64)),
        ("SPRITE_BRAWLERS", "brawlstars.png", BRAWLERS_REGION, True, BRAWLERS_REGION),
        ("SPRITE_BRAWLERS", "brawlstars.png", TRY_REGION, False, None),
        ("SPRITE_BRAWLERS", "brawlstars.png", TRY_REGION, True, None),
        ("SPRITE_BRAWLERS", "brawlstars.png", None, False, BRAWLERS_REGION),
        ("SPRITE_BRAWLERS", "brawlstars.png", None, True, BRAWLERS_REGION),
        # SPRITE_TRY visible in shelly.png (but not all regions)
        ("SPRITE_TRY", "shelly.png", APP_REGION, False, None),
        ("SPRITE_TRY", "shelly.png", APP_REGION, True, None),
        ("SPRITE_TRY", "shelly.png", BRAWLERS_REGION, False, None),
        ("SPRITE_TRY", "shelly.png", BRAWLERS_REGION, True, None),
        ("SPRITE_TRY", "shelly.png", TRY_REGION, False, (0, 0, 38, 190)),
        ("SPRITE_TRY", "shelly.png", TRY_REGION, True, TRY_REGION),
        ("SPRITE_TRY", "shelly.png", None, False, TRY_REGION),
        ("SPRITE_TRY", "shelly.png", None, True, TRY_REGION),
    ],
)
def test_locate(
    sprite_name, frame_filename, region, use_global_location, expected_location
):
    location = _locate_helper(sprite_name, frame_filename, region, use_global_location)
    assert location == expected_location


@pytest.mark.parametrize("sprite_name", ["SPRITE_APP"])
@pytest.mark.parametrize("frame_filename", ["shelly.png", "brawlstars.png"])
@pytest.mark.parametrize("region", [APP_REGION, BRAWLERS_REGION, TRY_REGION, None])
@pytest.mark.parametrize("use_global_location", [True, False])
def test_locate_template_no_sprite_app(
    sprite_name, frame_filename, region, use_global_location
):
    location = _locate_helper(sprite_name, frame_filename, region, use_global_location)
    assert location is None


@pytest.mark.parametrize("sprite_name", ["SPRITE_BRAWLERS"])
@pytest.mark.parametrize("frame_filename", ["shelly.png", "ldplayer.png"])
@pytest.mark.parametrize("region", [APP_REGION, BRAWLERS_REGION, TRY_REGION, None])
@pytest.mark.parametrize("use_global_location", [True, False])
def test_locate_template_no_sprite_brawlers(
    sprite_name, frame_filename, region, use_global_location
):
    location = _locate_helper(sprite_name, frame_filename, region, use_global_location)
    assert location is None


@pytest.mark.parametrize("sprite_name", ["SPRITE_TRY"])
@pytest.mark.parametrize("frame_filename", ["brawlstars.png", "ldplayer.png"])
@pytest.mark.parametrize("region", [APP_REGION, BRAWLERS_REGION, TRY_REGION, None])
@pytest.mark.parametrize("use_global_location", [True, False])
def test_locate_template_no_sprite_try(
    sprite_name, frame_filename, region, use_global_location
):
    location = _locate_helper(sprite_name, frame_filename, region, use_global_location)
    assert location is None
