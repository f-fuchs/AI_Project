import gymnasium as gym
import numpy as np
from gymnasium import spaces

from web_driver import DoodleJumpWebDriver


class DoodleJumpEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    last_score_frame = np.empty((50, 20))

    def __init__(self, frame_time, size):
        super(DoodleJumpEnv, self).__init__()

        self.dJWB = DoodleJumpWebDriver(frame_time)

        if size == "original":
            self.get_screenshot = self.dJWB.get_screenshot_grayscale_rescaled
        else:
            self.get_screenshot = self.dJWB.get_screenshot_grayscale
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions, we have two: left and right
        n_actions = 4
        self.action_space = spaces.Discrete(n_actions)
        self.actions = {
            0: self.dJWB.move_left,
            1: self.dJWB.move_right,
            2: self.dJWB.stay_still,
            3: self.dJWB.shoot,
        }

        # menu screen
        self.menu = np.load("menu.npy")

    def reset(self):
        """
        Important: the observation must be a numpy array
        :return: (np.array)
        """
        self.dJWB.restart_game()
        state = (
            np.array(self.get_screenshot(), dtype=np.single) / 255,
            np.array(self.get_screenshot(), dtype=np.single) / 255,
            np.array(self.get_screenshot(), dtype=np.single) / 255,
            np.array(self.get_screenshot(), dtype=np.single) / 255,
        )
        state = np.array(state)
        return state

    def step(self, action):
        # apply chosen action
        self.actions[action]()

        # calculate reward
        frame = self.get_screenshot()
        # frame.show()
        new_score_frame = np.array(frame.crop((0, 0, 50, 20)))
        if np.array_equal(new_score_frame, self.last_score_frame):
            reward = 1
        else:
            reward = 0
        self.last_score_frame = new_score_frame

        # check if done
        new_menu_frame = np.array(frame.crop((120, 210, 200, 250)))
        done = np.array_equal(new_menu_frame, self.menu)

        self.current_frame = frame
        state = (
            np.array(frame, dtype=np.single) / 255,
            np.array(self.get_screenshot(), dtype=np.single) / 255,
            np.array(self.get_screenshot(), dtype=np.single) / 255,
            np.array(self.get_screenshot(), dtype=np.single) / 255,
        )
        state = np.array(state)
        return state, reward, done

    def render(self, mode):
        if mode == "human":
            self.current_frame.show()
        elif mode == "rgb_array":
            return np.array(self.current_frame)

    def close(self):
        pass
