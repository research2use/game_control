import time

import cv2
import gym
import numpy as np
from gym import spaces
from gym.utils import seeding


class GameEnv(gym.Env):
    """Wrapper to make an OpenAI gym environment for a Game.

    Basically does three things:
        * Makes observation_space of the gym for a grabbed image of the game
        * Maps the possible keyboard events of the game to a discrete action
            space of the gym and vice versa
        * Redirects calls to the step and reset methods of the gym to the
            corresponding methods in the Game

    The wrapped game needs to define the following two methods:
        * step(self, action): returns observation, reward, terminal, info
        * reset(self): returns initial_observation

    """

    metadata = {"render.modes": ["human", "rgb_array"]}

    def __init__(self, game_class, **kwargs):
        """Construct/start the specified game and make observation and action spaces.

        Args:
            game_class (Game): Derived Game class with start() and stop()
                implementations that will be wrapped.
            **kwargs (dict): Additional arguments for the Game constructor.
        """
        self._game = game_class(**kwargs)
        self.viewer = None
        self._obs = None

        self.seed()

        (screen_width, screen_height) = self._game.observation_dimensions()
        print("game observation_dimensions = ", screen_width, screen_height)
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(screen_height, screen_width, 3), dtype=np.uint8
        )

        self._actions = self._game.actions
        self._action_count = len(self._actions)
        self.action_space = spaces.Discrete(self._action_count)

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        # Convert action from action_space to key of game
        assert self.action_space.contains(action)
        key_action = self._actions[action]

        self._obs, reward, done, info = self._game.step(key_action)

        return self._obs, reward, done, info

    def reset(self):
        return self._game.reset()

    def render(self, mode="human"):
        img = self._obs
        if img is None:
            return False
        elif mode == "rgb_array":
            return img
        elif mode == "human":
            print("Render img shape =", img.shape)
            # cv2.imshow("Viewer", img)
            # cv2.waitKey(1)
            # return True
            from gym.envs.classic_control import rendering

            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(img)
            return self.viewer.isopen

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None
