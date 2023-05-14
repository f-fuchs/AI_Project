import time
from io import BytesIO
import base64
import numpy as np
from PIL import Image, ImageOps
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class DoodleJumpWebDriver:
    def __init__(self, frame_time):
        self.frame_time = frame_time
        self.url = "https://doodle-jump.io/game/doodle-jump/"
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=200,300")
        self.driver = webdriver.Chrome("chromedriver", options=options)
        # self.driver.get(self.url)
        self.action_chains = ActionChains(self.driver)
        self.action_chain_left = (
            self.action_chains.key_down(Keys.ARROW_LEFT)
            .pause(frame_time)
            .key_up(Keys.ARROW_LEFT)
        )
        self.action_chain_right = (
            self.action_chains.key_down(Keys.ARROW_RIGHT)
            .pause(frame_time)
            .key_up(Keys.ARROW_RIGHT)
        )
        self.action_chain_shoot = (
            self.action_chains.key_down(Keys.ARROW_UP)
            .pause(frame_time)
            .key_up(Keys.ARROW_UP)
        )

        self.play = np.load("play.npy")

    def get_screenshot(self):
        image_b64 = self.driver.get_screenshot_as_base64()
        screen = Image.open(BytesIO(base64.b64decode(image_b64)))
        return screen

    def get_screenshot_grayscale(self):
        return ImageOps.grayscale(self.get_screenshot())

    def get_screenshot_grayscale_rescaled(self):
        return ImageOps.grayscale(self.get_screenshot()).resize((84, 84))

    def start_game(self):
        elem_canvas = self.driver.find_element(By.XPATH, "/html/body/canvas")
        self.action_chains.move_to_element(elem_canvas).move_by_offset(
            -10, -75
        ).click().perform()

    def restart_game(self):
        def __contains_play_button():
            loading_frame = np.array(
                self.get_screenshot_grayscale().crop((40, 72, 110, 97))
            )
            return np.array_equal(loading_frame, self.play)

        while True:
            self.driver.get(self.url)
            # np.save("play.npy", np.array(self.get_screenshot_grayscale().crop((40, 72, 110, 97))))
            i = 0
            while i < 50 and not __contains_play_button():
                time.sleep(0.1)
                i += 1
            if i < 50:
                self.start_game()
                return

    def move_left(self):
        self.action_chains.key_down(Keys.ARROW_LEFT).pause(self.frame_time).key_up(
            Keys.ARROW_LEFT
        ).perform()

    def move_right(self):
        self.action_chains.key_down(Keys.ARROW_RIGHT).pause(self.frame_time).key_up(
            Keys.ARROW_RIGHT
        ).perform()

    def stay_still(self):
        time.sleep(self.frame_time)

    def shoot(self):
        self.action_chains.key_down(Keys.ARROW_UP).pause(self.frame_time).key_up(
            Keys.ARROW_UP
        ).perform()
