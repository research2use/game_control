class Frame:
    """Frame of a game.

    Class to hold an image with some additional info.

    """

    def __init__(self, img, timestamp=None):
        """Construct frame and fill with given arguments.

        Args:
            img (np.ndarray): array with pixel values.
            timestamp (datetime): date and time of creation.

        """
        self.img = img
        self.timestamp = timestamp
