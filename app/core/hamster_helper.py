from logging_config import logger

import os
import re
import time
import random
import threading
from functools import wraps

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import (NoSuchElementException,
                                        ElementNotInteractableException,
                                        ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        TimeoutException,
                                        NoSuchWindowException,
                                        WebDriverException)

from .base_helper import BaseHelper


base_path = os.path.dirname(__file__)


class HamsterHelper(BaseHelper):
    @BaseHelper.handle_exceptions
    def __init__(self, name, src, platform, timeout, num_clicks, headless, claim_daily_rewards):
        super().__init__(headless=headless)
        self.stop_event = threading.Event()
        self.base_url = self.rewrite_html(name, src, platform)
        self.timeout = timeout
        self.num_clicks = num_clicks
        self.claim_daily_rewards = claim_daily_rewards

        if self.base_url:
            self.driver.get(self.base_url)
            self.driver.set_window_rect(width=300, height=800)
            self.switch_to_iframe()
        else:
            self.stop_event.set()
            logger.error(f'Для пользователя [{name}] неверно указан src: {src}')

    @staticmethod
    def check_stop_event(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.stop_event.is_set():
                return
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def rewrite_html(name, src, platform) -> str:
        """ Перезаписать src в шаблоне html."""
        def extract_url(s):
            match = re.search(r'src=["\']?([^"\'>\s]+)["\']?|([^"\'>\s]+)', s)
            if match:
                return match.group(1) or match.group(2)
            return None

        src = extract_url(src)

        html_template_path = os.path.join(base_path, "hamster.html")
        accounts_dir = os.path.join(base_path, 'accounts')
        os.makedirs(accounts_dir, exist_ok=True)
        html_user_path = os.path.join(accounts_dir, f"{name}.html")

        if re.search(r'tgWebAppPlatform=(web|ios|android|android_x)', src):
            new_src = re.sub(r'tgWebAppPlatform=(web|ios|android|android_x)', f'tgWebAppPlatform={platform}', src)

            with open(html_template_path, "r", encoding="utf-8") as file:
                html_template_content = file.read()

            html_content = re.sub(r'src="[^"]*"', f'src="{new_src}"', html_template_content)

            with open(html_user_path, "w", encoding="utf-8") as file:
                file.write(html_content)

            return html_user_path

    @staticmethod
    def block_sites(driver, blocked_urls: list):
        """ Заблокировать переход на список сайтов. """
        blocked_urls_script = ", ".join(f"'{url}'" for url in blocked_urls)

        script = f"""
                    (function() {{
                        var originalOpen = window.open;
                        window.open = function(url, name, specs) {{
                            var blockedUrls = [{blocked_urls_script}];
                            for (var i = 0; i < blockedUrls.length; i++) {{
                                if (url.includes(blockedUrls[i])) {{
                                    console.log('Blocked attempt to open URL: ' + url);
                                    return null;
                                }}
                            }}
                            return originalOpen.apply(this, arguments);
                        }};
                    }})();
                """

        driver.execute_script(script)

    @check_stop_event
    @BaseHelper.handle_exceptions
    def switch_to_iframe(self):
        """ Переключится в iframe хомяка. """
        iframe = WebDriverWait(self.driver, self.timeout + 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'payment-verification'))
        )
        self.driver.switch_to.frame(iframe)

        user_info_element = WebDriverWait(self.driver, self.timeout + 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.user-info p'))
        )
        hamster_username = user_info_element.text

        logger.info(f"Успешный вход в Hamster Kombat {hamster_username}!")

    @check_stop_event
    @BaseHelper.handle_exceptions
    def exchange_or_level_window(self):
        """ Всплывающее окно при получении дохода от биржи при повышении уровня. """
        try:
            exchange_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'bottom-sheet-button.button.button-primary.button-large'))
            )
            exchange_button.click()

            logger.info(f"Биржа принесла доход или повысился уровень.")
            return True

        except TimeoutException:
            pass

    @check_stop_event
    @BaseHelper.handle_exceptions
    def back_to_main_page(self):
        """ Возвращаемся на главую страницу. """
        try:
            bar_buttons = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '.app-bar-item.no-select'))
            )
            bar_buttons[0].click()

        except TimeoutException:
            pass

    @check_stop_event
    @BaseHelper.handle_exceptions
    def use_energy_boost(self):
        """ Используем бустеры энергии если они есть. """
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            boosts_button = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'user-tap-boost'))
            )
            boosts_button.click()

            boosts_columns = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'boost-column'))
            )

            boosts = WebDriverWait(boosts_columns[0], self.timeout).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'boost-item'))
            )
            boosts.click()

            confirm_button = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'bottom-sheet-button.button.button-primary.button-large'))
            )
            confirm_button.click()

            logger.info(f"Был использован бустер энергии.")
            return True

        except (TimeoutException, ElementClickInterceptedException, ElementNotInteractableException):
            self.back_to_main_page()
            logger.info(f"Нет доступного бустера энергии.")
            return False

    @check_stop_event
    @BaseHelper.handle_exceptions
    def tap_tap(self):
        """ Начать нажимать по кнопке. """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        hamster_button = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'user-tap-button.button'))
        )

        logger.info(f"Добыча монет в Hamster Kombat запущена.")

        for _ in range(self.num_clicks):
            try:
                if self.stop_event.is_set():
                    break
                else:
                    hamster_button.click()
                    time.sleep(random.randint(1, 10) / 100)

            except (ElementNotInteractableException, ElementClickInterceptedException):
                self.exchange_or_level_window()

        logger.info(f"Добыча монет Hamster Kombat завершёна.")

        if self.use_energy_boost():
            self.tap_tap()

    @check_stop_event
    @BaseHelper.handle_exceptions
    def claim_rewards(self):
        """ Собрать монеты со всех ежедневных активностей. """
        activities = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.user-attraction-item, .user-attraction-item.is-completed'))
        )
        activities[0].click()

        self.block_sites(driver=self.driver,
                         blocked_urls=["youtu.be", "youtube.com",
                                       "facebook.com",
                                       "instagram.com",
                                       "twitter.com", "x.com"])

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        try:
            earn_column = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'earn-column'))
            )

            for column in earn_column:
                earn_items = WebDriverWait(column, self.timeout).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, 'earn-item'))
                )

                for item in earn_items:
                    if self.stop_event.is_set:
                        return

                    try:
                        item.click()
                    except ElementClickInterceptedException:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        item.click()

                    try:
                        claim_button = WebDriverWait(self.driver, self.timeout).until(
                            EC.element_to_be_clickable(
                                (By.CLASS_NAME, 'bottom-sheet-button.button.button-primary.button-large'))
                        )
                        claim_button.click()
                    except TimeoutException:
                        pass

                    try:
                        close_button = WebDriverWait(self.driver, self.timeout).until(
                            EC.element_to_be_clickable(
                                (By.CLASS_NAME, 'bottom-sheet-close'))
                        )
                        close_button.click()
                    except TimeoutException:
                        pass

        finally:
            self.back_to_main_page()
            logger.info(f"Ежедневные награды собраны.")

    @check_stop_event
    @BaseHelper.handle_exceptions
    def play_morse(self):
        """ Пройти ежедневную игру Морзе. """
        pass

    @check_stop_event
    def start(self):
        """ Начать добывать монеты пока не будет установлено событие остановки. """
        end_time = 0
        attempts = 0

        while not self.stop_event.is_set():
            try:
                self.exchange_or_level_window()

                if self.claim_daily_rewards and time.time() > end_time:
                    self.claim_rewards()
                    end_time = time.time() + 12 * 60 * 60

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                energy_limit = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.user-tap-energy p'))
                )
                # energy_limit динамически изменяющаяся величина,
                # которая может быть пустой если потратить всю энергию
                while not energy_limit.text:
                    time.sleep(2)

                current_energy_balance, max_energy_limit = energy_limit.text.split('/')
                current_energy_balance = int(current_energy_balance.strip())
                max_energy_limit = int(max_energy_limit.strip())
                logger.info(f"Текущий баланс энергии: {current_energy_balance}")

                if current_energy_balance > max_energy_limit - max_energy_limit * 0.25:
                    self.tap_tap()
                else:
                    wait_time = time.time() + max_energy_limit * (30 / 100)
                    while time.time() < wait_time:
                        if self.stop_event.is_set():
                            break
                        time.sleep(1)

            except NoSuchWindowException:
                self.stop_event.set()
                break

            except KeyboardInterrupt:
                self.stop_event.set()
                break

            except Exception as e:
                logger.error(f"Поймана ошибка: {e}", exc_info=True)
                attempts += 1
                logger.warning(f"Что то пошло не так и пользователь был перезапущен {attempts} раз.")
                self.driver.refresh()
                self.switch_to_iframe()

        self.close()


MORSE_CODE_DICT = {'A': '.-', 'B': '-...',
                   'C': '-.-.', 'D': '-..', 'E': '.',
                   'F': '..-.', 'G': '--.', 'H': '....',
                   'I': '..', 'J': '.---', 'K': '-.-',
                   'L': '.-..', 'M': '--', 'N': '-.',
                   'O': '---', 'P': '.--.', 'Q': '--.-',
                   'R': '.-.', 'S': '...', 'T': '-',
                   'U': '..-', 'V': '...-', 'W': '.--',
                   'X': '-..-', 'Y': '-.--', 'Z': '--..',
                   '1': '.----', '2': '..---', '3': '...--',
                   '4': '....-', '5': '.....', '6': '-....',
                   '7': '--...', '8': '---..', '9': '----.',
                   '0': '-----', ', ': '--..--', '.': '.-.-.-',
                   '?': '..--..', '/': '-..-.', '-': '-....-',
                   '(': '-.--.', ')': '-.--.-'}
