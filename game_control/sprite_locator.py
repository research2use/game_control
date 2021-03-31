from game_control.sprite import Sprite


class SpriteLocator:

    def __init__(self, **kwargs):
        pass

    @classmethod
    def _extract_region_from_image(image, region_bounding_box):
        return image[region_bounding_box[0]:region_bounding_box[2],
                     region_bounding_box[1]:region_bounding_box[3]]

    def locate(self,
               sprite=None,
               frame=None,
               screen_region=None,
               use_global_location=True):
        """
        Locates the sprite within the defined game frame

        Parameters
            sprite: The sprite to find\n
            frame: The frame to search within\n
            screen_region: (optional) region within which to search within the frame\n
            use_global_location: (optional) if using a region, whether to return global location or local to region

        Returns
            Tuple of location of the sprite
        """
        constellation = sprite.generate_constellation_of_pixels_images()
        location = None

        img = frame.img

        if screen_region:
            img = self._extract_region_from_image(img, screen_region)

        for i in range(len(constellation)):
            constellation_of_pixels_item = list(sprite.constellation_of_pixels[i].items())[0]

            query_coordinates = constellation_of_pixels_item[0]
            query_rgb = constellation_of_pixels_item[1]

            rgb_coordinates = Sprite.locate_color(query_rgb, image=img)

            rgb_coordinates = list(map(lambda yx: (yx[0] - query_coordinates[0], yx[1] - query_coordinates[1]), rgb_coordinates))

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
                        x + constellation[i].shape[1]
                    )

        if location and screen_region and use_global_location:
            location = (
                location[0] + screen_region[0],
                location[1] + screen_region[1],
                location[2] + screen_region[0],
                location[3] + screen_region[1]
            )

        return location
