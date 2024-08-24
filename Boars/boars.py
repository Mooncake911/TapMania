import os
import sys

import time
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# Params
YANDEX_USERNAME = "username"
TAP_COUNT = 4000


# Logging settings
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


class TapHelper:
    _instance = None

    driver_path = '../Hamsters/app/core/chromedriver-win64/chromedriver.exe'
    base_url = 'https://ya.ru/search/?text=%D0%BA%D0%B0%D0%B1%D0%B0%D0%BD&lr=50'

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_driver(*args, **kwargs)
        return cls._instance

    def _init_driver(self, *args, **kwargs):
        try:
            options = Options()
            # options.add_argument("--headless=new")
            # options.add_argument("--disable-css")  # отключаем css
            # # Отключение автоматического загрузчика изображений
            # options.add_argument("--disable-extensions")
            # options.add_argument("--disable-plugins-discovery")
            # # Отключаем защиту браузера
            # options.add_argument("--disable-web-security")
            # options.add_argument("--allow-running-insecure-content")
            service = Service(executable_path=self.driver_path)
            self.driver = webdriver.Chrome(options=options, service=service)
            logger.info(f"Chrome driver успешно инициализирован.")
            self.driver.get(self.base_url)

        except Exception as ex:
            logger.error(f"Ошибка инициализации Chrome driver:\n{ex}")

    def stop(self):
        if self.driver:
            self.driver.close()
            self.driver.quit()
        logger.info(f"Chrome driver был остановлен.")

    def login(self):
        try:
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME,
                                            "HeaderDesktopLink.HeaderDesktopLink_type_login.HeaderDesktopLogin-Login"))
            )
            login_button.click()
            time.sleep(1)

            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "passp-field-login"))
            )
            username_input.clear()
            username_input.send_keys(YANDEX_USERNAME)
            time.sleep(1)

            while self.driver.current_url.startswith('https://passport.yandex.ru'):
                pass

            logger.info(f"Вы успешно вошли в личный кабинет Yandex.")

        except Exception as ex:
            logger.error(f"Ошибка входа в yandex:\n{ex}")

    def start_tap(self):
        try:
            main_event = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME,
                                            "EasterEggFab.EasterEggFab_position_none.EasterEggFab_ready"))
            )
            data_clicks = main_event.get_attribute("data-clicks")

            tap_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME,
                                            "Button2.Button2_pin_circle-circle.EasterEggFab-Button.EasterEggControls-Control.EasterEggControls-Control_type_fab"))
            )

            while int(data_clicks) <= TAP_COUNT:
                tap_button.click()
                data_clicks = main_event.get_attribute("data-clicks")
            time.sleep(1)

            stop_button_1 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME,
                                            "Button2.Button2_pin_circle-circle.EasterEggControls-Control.EasterEggControls-Control_type_close"))
            )
            stop_button_1.click()
            time.sleep(1)

            stop_button_2 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME,
                                            "Button2.Button2_size_l.Button2_view_default.Button2_pin_circle-circle.EasterEggModal-Control"))
            )
            stop_button_2.click()
            time.sleep(10)

            logger.info(f"Гонение кабанов успешно завершено.")

        except Exception as ex:
            logger.error(f"Какая-то ошибка в тапалке:\n{ex}")


if __name__ == '__main__':
    my_tap_tool = TapHelper()
    my_tap_tool.login()
    my_tap_tool.start_tap()
    my_tap_tool.stop()
