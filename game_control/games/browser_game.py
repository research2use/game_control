import webbrowser

from game_control.game import Game


class BrowserGame(Game):
    """Implementation of abstract base class to control a browser game."""

    def __init__(self, url, browser=None, **kwargs):
        """Constructs and starts and game in a webrowser.

        Args:
            url (str): web address of the game
            browser (str): start game in the given browser, which needs to be
                registered: https://docs.python.org/3/library/webbrowser.html
                Defaults to the default browser on your system.

        """
        self._url = url
        self._browser = browser
        super().__init__(**kwargs)

    def start(self):
        """Start url of the game in awebbrowser."""
        self._process = webbrowser.get(self._browser).open_new(self._url)

    def stop(self):
        """Does nothing actually; you need to close the game by hand."""
        pass
