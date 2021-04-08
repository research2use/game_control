import random
import uuid
from pathlib import Path

import cv2
import numpy as np

from game_control.utilities import extract_roi_from_image


class SpriteError(BaseException):
    pass


class Sprite:
    def __init__(
        self, name, image_data=None, signature_colors=None, constellation_of_pixels=None
    ):
        if not isinstance(image_data, np.ndarray):
            raise SpriteError("'image_data' needs to be a 4D instance of ndarray...")

        if not len(image_data.shape) == 4:
            raise SpriteError("'image_data' ndarray needs to be 4D...")

        self.name = name
        self.image_data = image_data
        self.image_shape = image_data.shape[:2]
        self.image_count = image_data.shape[-1]

        self.signature_colors = signature_colors or self._generate_signature_colors()

        self.constellation_of_pixels = (
            constellation_of_pixels or self._generate_constellation_of_pixels()
        )

    def append_image_data(
        self, image_data, signature_colors=None, constellation_of_pixels=None
    ):
        images = list()

        for i in range(self.image_data.shape[3]):
            images.append((self.image_data[:, :, :, i])[:, :, :, np.newaxis])

        images.append(image_data)

        self.image_data = np.squeeze(np.stack(images, axis=3))

        if signature_colors is not None:
            self.signature_colors.append(signature_colors)
        else:
            self.signature_colors = self._generate_signature_colors()

        if constellation_of_pixels is not None:
            self.constellation_of_pixels.append(constellation_of_pixels)
        else:
            self.constellation_of_pixels = self._generate_constellation_of_pixels()

    def generate_constellation_of_pixels_images(self):
        constellation_of_pixel_images = list()

        for i in range(self.image_data.shape[3]):
            constellation_of_pixel_image = np.zeros(
                self.image_data[..., :3, 0].shape, dtype="uint8"
            )

            for yx, rgb in self.constellation_of_pixels[0].items():
                constellation_of_pixel_image[yx[0], yx[1], :] = rgb

            constellation_of_pixel_images.append(constellation_of_pixel_image)

        return constellation_of_pixel_images

    def _generate_seed(self):
        return str(uuid.uuid4())

    def _generate_signature_colors(self, quantity=8):
        signature_colors = list()
        height, width, pixels, animation_states = self.image_data.shape

        for i in range(animation_states):
            values, counts = np.unique(
                self.image_data[..., i].reshape(width * height, pixels),
                axis=0,
                return_counts=True,
            )

            if len(values[0]) == 3:
                maximum_indices = np.argsort(counts)[::-1][:quantity]
            elif len(values[0]) == 4:
                maximum_indices = list()

                for index in np.argsort(counts)[::-1]:
                    value = values[index]

                    if value[3] > 0:
                        maximum_indices.append(index)

                        if len(maximum_indices) == quantity:
                            break

            colors = [tuple(map(int, values[index][:3])) for index in maximum_indices]
            signature_colors.append(set(colors))

        return signature_colors

    def _generate_constellation_of_pixels(self, quantity=8):
        constellation_of_pixels = list()
        height, width, pixels, animation_states = self.image_data.shape

        for i in range(animation_states):
            constellation_of_pixels.append(dict())

            for ii in range(quantity):
                signature_color = random.choice(list(self.signature_colors[i]))
                signature_color_locations = Sprite.locate_color(
                    signature_color, np.squeeze(self.image_data[:, :, :3, i])
                )

                y, x = random.choice(signature_color_locations)
                constellation_of_pixels[i][(y, x)] = signature_color

        return constellation_of_pixels

    @classmethod
    def locate_color(cls, color, image):
        # TODO: Optimize for ms gain

        if image.shape[2] == 3:
            color_indices = np.where(np.all(image[:, :, :3] == color, axis=-1))
        elif image.shape[2] == 4:
            color_indices = np.where(
                np.all(image[:, :, :3] == (list(color) + [255]), axis=-1)
            )

        return list(zip(*color_indices)) if len(color_indices[0]) else list()

    @staticmethod
    def locate(sprite=None, frame=None, region=None, use_global_location=True):
        """
        Locates the sprite within the defined (roi of) frame.

        Args:
            sprite (Sprite): The sprite to find.
            frame (Frame): The frame to search within.
            region (tuple): Only search within this region of the frame.
            use_global_location (bool): if using a region, whether to return
                global location or local to region.

        Returns:
            Tuple of location of the sprite when found or None otherwise.
        """
        constellation = sprite.generate_constellation_of_pixels_images()
        location = None

        img = frame.img

        if region:
            img = extract_roi_from_image(img, region)

        for i in range(len(constellation)):
            constellation_of_pixels_item = list(
                sprite.constellation_of_pixels[i].items()
            )[0]

            query_coordinates = constellation_of_pixels_item[0]
            query_rgb = constellation_of_pixels_item[1]

            rgb_coordinates = Sprite.locate_color(query_rgb, image=img)

            rgb_coordinates = list(
                map(
                    lambda yx: (
                        yx[0] - query_coordinates[0],
                        yx[1] - query_coordinates[1],
                    ),
                    rgb_coordinates,
                )
            )

            maximum_y = img.shape[0] - constellation[i].shape[0]
            maximum_x = img.shape[1] - constellation[i].shape[1]

            for y, x in rgb_coordinates:
                if y < 0 or x < 0 or y > maximum_y or x > maximum_x:
                    continue

                for yx, rgb in sprite.constellation_of_pixels[i].items():
                    if tuple(img[y + yx[0], x + yx[1], :]) != rgb:
                        break
                else:
                    location = (
                        y,
                        x,
                        y + constellation[i].shape[0],
                        x + constellation[i].shape[1],
                    )

        if location and region and use_global_location:
            location = (
                location[0] + region[0],
                location[1] + region[1],
                location[2] + region[0],
                location[3] + region[1],
            )

        return location

    @staticmethod
    def locate_template(
        sprite=None,
        frame=None,
        region=None,
        use_global_location=True,
        match_method=cv2.TM_CCORR_NORMED,
        match_threshold=0.95,
    ):
        """
        Locates the sprite within the defined (roi of) frame.

        Args:
            sprite (Sprite): The sprite to find.
            frame (Frame): The frame to search within.
            region (tuple): Only search within this region of the frame.
            use_global_location (bool): if using a region, whether to return
                global location or local to region.

        Returns:
            Tuple of location of the sprite when found or None otherwise.
        """
        img = frame.img
        if region:
            img = extract_roi_from_image(img, region)

        if img.shape[0] < sprite.image_shape[0] or img.shape[1] < sprite.image_shape[1]:
            return None

        best = None
        for s in range(sprite.image_count):
            match_result = cv2.matchTemplate(
                img, sprite.image_data[..., s], match_method
            )
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result, None)
            if match_method == cv2.TM_SQDIFF or match_method == cv2.TM_SQDIFF_NORMED:
                if min_val <= match_threshold:
                    if best is None or min_val < best[0]:
                        best = (min_val, min_loc)
            else:
                if max_val >= match_threshold:
                    if best is None or max_val >= best[0]:
                        best = (max_val, max_loc)

        location = None
        if best is not None:
            best_loc = best[1]
            location = (
                best_loc[1],
                best_loc[0],
                best_loc[1] + sprite.image_shape[0],
                best_loc[0] + sprite.image_shape[1],
            )

        if location and region and use_global_location:
            location = (
                location[0] + region[0],
                location[1] + region[1],
                location[2] + region[0],
                location[3] + region[1],
            )

        return location

    @staticmethod
    def discover_sprites(sprites_dir):
        """Discover the sprites in the given dir (of a game).

        Args:
            sprites_dir (Path/str): Directory where to search for sprites.

        Returns:
            dict: key value pairs where keys are sprite name strings and values
                are Sprite objects with the pixel data of one or more images.
        """
        sprites = {}
        sprites_dir = Path(sprites_dir)

        if sprites_dir.is_dir():
            for file_path in sprites_dir.glob("*.png"):
                sprite_name = "_".join(str(file_path.stem).split("_")[:-1]).upper()

                sprite_image_data = cv2.imread(str(file_path))
                sprite_image_data = sprite_image_data[..., np.newaxis]

                if sprite_name not in sprites:
                    sprite = Sprite(sprite_name, image_data=sprite_image_data)
                    sprites[sprite_name] = sprite
                else:
                    sprites[sprite_name].append_image_data(sprite_image_data)

        return sprites
