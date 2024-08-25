import re
import time
import random

from pathlib import Path

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


from app.core.base_helper import BaseHelper
from app.core.logging_config import logger


class HamsterHelper(BaseHelper):
    @BaseHelper.handle_exceptions
    def __init__(self, name, src, platform, timeout, num_clicks, show):
        super().__init__(show=show)
        self.base_url = self.rewrite_html(name, src, platform)
        self.timeout = timeout
        self.num_clicks = num_clicks

        self.driver.get(self.base_url)
        self.driver.set_window_rect(width=300, height=800)
        self.switch_to_iframe()

    @staticmethod
    def rewrite_html(name, src, platform) -> str:
        """ Перезаписать src в шаблоне html."""
        with open(Path("hamster.html").absolute().as_posix(), "r", encoding="utf-8") as file:
            html_content = file.read()

        if 'tgWebAppPlatform=web' in src:
            new_src = src.replace('tgWebAppPlatform=web', f'tgWebAppPlatform={platform}')
            html_content = re.sub(r'src="[^"]*"', f'src="{new_src}"', html_content)

            new_html_path = Path(f"accounts/{name}.html")
            with open(new_html_path, "w", encoding="utf-8") as file:
                file.write(html_content)

            return new_html_path.absolute().as_posix()

        else:
            raise NoSuchElementException

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

    @BaseHelper.handle_exceptions
    def switch_to_iframe(self):
        iframe = WebDriverWait(self.driver, self.timeout + 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'payment-verification'))
        )
        self.driver.switch_to.frame(iframe)

        user_info_element = WebDriverWait(self.driver, self.timeout + 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.user-info p'))
        )
        hamster_username = user_info_element.text

        logger.info(f"Успешный вход в Hamster Kombat {hamster_username}")

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
            logger.info(f"Нет доступного бустера энергии.")
            return False

        finally:
            self.back_to_main_page()

    @BaseHelper.handle_exceptions
    def tap_tap(self):
        """ Начать нажимать по кнопке. """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        hamster_button = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'user-tap-button.button'))
        )

        logger.info(f"Фарм монет в Hamster Kombat запущен.")

        for _ in range(self.num_clicks):
            try:
                hamster_button.click()
                time.sleep(random.randint(1, 10) / 100)

            except (ElementNotInteractableException, ElementClickInterceptedException):
                self.exchange_or_level_window()

        logger.info(f"Фарм монет Hamster Kombat завершён.")

        if self.use_energy_boost():
            self.tap_tap()

    @staticmethod
    def block_sites(driver, blocked_urls: list):
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

    @BaseHelper.handle_exceptions
    def play_morse(self):
        """ Пройти ежедневную игру в Морзе. """
        pass

    def start(self, stop_event):
        end_time = 0
        attempts = 0

        while not stop_event.is_set():
            try:
                self.exchange_or_level_window()

                if time.time() > end_time:
                    self.claim_rewards()
                    end_time = time.time() + 2 * 60 * 60

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
                    time.sleep(max_energy_limit * (30 / 100))

            except NoSuchWindowException:
                break

            except KeyboardInterrupt:
                break

            except Exception as e:
                logger.error(f"Caught exception: {e}")
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
