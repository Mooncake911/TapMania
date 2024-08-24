import re
import sys
import time
import random
import logging
import threading

from pathlib import Path
from functools import wraps

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

from urllib3.exceptions import NewConnectionError, MaxRetryError


# Params
LOG_LEVEL = 'INFO'
TIMEOUT = 10
NUM_CLICKS = 500
PLATFORM = "android"
SHOW = False


# Logging settings
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Logging to file
file_handler = logging.FileHandler('hamster.log', mode='w')
file_handler.setLevel(LOG_LEVEL)
file_formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                   datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Logging to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOG_LEVEL)
console_formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


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


class SeleniumHelper(object):
    driver_path = Path('chromedriver-win64/chromedriver.exe')

    def __init__(self):
        options = Options()
        if not SHOW:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--log-level=3')

        service = Service(executable_path=self.driver_path.absolute().as_posix())
        self.driver = webdriver.Chrome(service=service, options=options)

        logger.info(f"Chrome driver успешно инициализирован.")

    @staticmethod
    def handle_exceptions(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except NoSuchElementException:
                logger.error(f"Элемент не найден.", exc_info=True)
            except ElementNotInteractableException:
                logger.error(f"Элемент найден, но не доступен для взаимодействия.", exc_info=True)
            except ElementClickInterceptedException:
                logger.error(f"Не удалось кликнуть на элемент.", exc_info=True)
            except StaleElementReferenceException:
                logger.error(f"Элемент устарел.", exc_info=True)
            except TimeoutException:
                logger.error(f"Время ожидания истекло.", exc_info=True)
            except NoSuchWindowException:
                logger.warning(f"Окно браузера было закрыто.")
                sys.exit(0)
            except WebDriverException:
                logger.error(f"Ошибка WebDriver.")
                sys.exit(1)
            except (KeyboardInterrupt, MaxRetryError, NewConnectionError):
                logger.error(f"Программа остановлена.")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Неизвестная ошибка.\n{e}", exc_info=True)
                sys.exit(1)

        return wrapper

    def close(self):
        """ Остановка Webdriver. """
        if self.driver:
            self.driver.close()
            self.driver.quit()

        logger.info(f"Chrome driver был остановлен.")


class TapHelper(SeleniumHelper):
    @SeleniumHelper.handle_exceptions
    def __init__(self, name, src, stop_event):
        super().__init__()
        self.stop_event = stop_event

        self.base_url = self.rewrite_html(name, src)
        self.driver.get(self.base_url)
        self.driver.set_window_rect(width=300, height=800)
        self.switch_to_iframe()

    @staticmethod
    def rewrite_html(name, src):
        """ Перезаписать src в шаблоне html."""
        with open(Path("hamsters.html").absolute().as_posix(), "r", encoding="utf-8") as file:
            html_content = file.read()

        if 'tgWebAppPlatform=web' in src:
            new_src = src.replace('tgWebAppPlatform=web', f'tgWebAppPlatform={PLATFORM}')
            html_content = re.sub(r'src="[^"]*"', f'src="{new_src}"', html_content)

            new_html_path = Path(f"accounts/{name}.html")
            with open(new_html_path, "w", encoding="utf-8") as file:
                file.write(html_content)

            return new_html_path.absolute().as_posix()

        else:
            raise NoSuchElementException

    @SeleniumHelper.handle_exceptions
    def exchange_or_level_window(self):
        """ Всплывающее окно при получении дохода от биржи при повышении уровня. """
        try:
            exchange_button = WebDriverWait(self.driver, TIMEOUT).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'bottom-sheet-button.button.button-primary.button-large'))
            )
            exchange_button.click()

            logger.info(f"Биржа принесла доход или повысился уровень.")
            return True

        except TimeoutException:
            pass

    @SeleniumHelper.handle_exceptions
    def back_to_main_page(self):
        """ Возвращаемся на главую страницу. """
        try:
            bar_buttons = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '.app-bar-item.no-select'))
            )
            bar_buttons[0].click()

        except TimeoutException:
            pass

    @SeleniumHelper.handle_exceptions
    def switch_to_iframe(self):
        iframe = WebDriverWait(self.driver, TIMEOUT + 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'payment-verification'))
        )
        self.driver.switch_to.frame(iframe)

        user_info_element = WebDriverWait(self.driver, TIMEOUT + 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.user-info p'))
        )
        hamster_username = user_info_element.text

        logger.info(f"Успешный вход в Hamster Kombat {hamster_username}")

    @SeleniumHelper.handle_exceptions
    def use_energy_boost(self):
        """ Используем бустеры энергии если они есть. """
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            boosts_button = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'user-tap-boost'))
            )
            boosts_button.click()

            boosts_columns = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'boost-column'))
            )

            boosts = WebDriverWait(boosts_columns[0], TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'boost-item'))
            )
            boosts.click()

            confirm_button = WebDriverWait(self.driver, TIMEOUT).until(
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

    @SeleniumHelper.handle_exceptions
    def tap_tap(self):
        """ Начать нажимать по кнопке. """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        hamster_button = WebDriverWait(self.driver, TIMEOUT).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'user-tap-button.button'))
        )

        logger.info(f"Фарм монет в Hamster Kombat запущен.")

        for _ in range(NUM_CLICKS):
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

    @SeleniumHelper.handle_exceptions
    def claim_rewards(self):
        """ Собрать монеты со всех ежедневных активностей. """
        activities = WebDriverWait(self.driver, TIMEOUT).until(
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
            earn_column = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'earn-column'))
            )

            for column in earn_column:
                earn_items = WebDriverWait(column, TIMEOUT).until(
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
                        claim_button = WebDriverWait(self.driver, TIMEOUT).until(
                            EC.element_to_be_clickable(
                                (By.CLASS_NAME, 'bottom-sheet-button.button.button-primary.button-large'))
                        )
                        claim_button.click()
                    except TimeoutException:
                        pass

                    try:
                        close_button = WebDriverWait(self.driver, TIMEOUT).until(
                            EC.element_to_be_clickable(
                                (By.CLASS_NAME, 'bottom-sheet-close'))
                        )
                        close_button.click()
                    except TimeoutException:
                        pass

        finally:
            self.back_to_main_page()
            logger.info(f"Ежедневные награды собраны.")

    @SeleniumHelper.handle_exceptions
    def play_morse(self):
        """ Пройти ежедневную игру в Морзе. """
        pass

    def start(self):
        logger.info(f"Программа Hamster Kombat Farm запущена.")

        end_time = 0
        attempts = 0

        while not self.stop_event.is_set():
            try:
                self.exchange_or_level_window()

                if time.time() > end_time:
                    self.claim_rewards()
                    end_time = time.time() + 2 * 60 * 60

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                energy_limit = WebDriverWait(self.driver, TIMEOUT).until(
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
                    time.sleep(max_energy_limit * (33 / 100))

            except KeyboardInterrupt:
                break

            except NoSuchWindowException:
                break

            except Exception as e:
                # logger.error(f"Caught exception: {e}")
                attempts += 1
                logger.warning(f"Что то пошло не так и программа была перезапущена {attempts} раз.")
                self.driver.refresh()
                self.switch_to_iframe()

        self.close()
        logger.info(f"Программа Hamster Kombat Farm завершена.")


if __name__ == '__main__':

    def interact_with_page(name, src, stop_event):
        tap_halper = TapHelper(name=name, src=src, stop_event=stop_event)
        tap_halper.start()

    nasty = ("Nasty", "https://hamsterkombat.io/clicker#tgWebAppData=query_id%3DAAHDoJNgAAAAAMOgk2D94HHZ%26user%3D%257B%2522id%2522%253A1620287683%252C%2522first_name%2522%253A%2522Melissa%2522%252C%2522last_name%2522%253A%2522Pushina%2522%252C%2522username%2522%253A%2522Melissa_pushina%2522%252C%2522language_code%2522%253A%2522ru%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1724428431%26hash%3D164395524ec2cb7fa42b6b96ceecda4c561e3378393b2876c83af2028af40bb7&tgWebAppVersion=7.6&tgWebAppPlatform=web&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%233390ec%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23707579%22%2C%22link_color%22%3A%22%2300488f%22%2C%22secondary_bg_color%22%3A%22%23f4f4f5%22%2C%22text_color%22%3A%22%23000000%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22accent_text_color%22%3A%22%233390ec%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%233390ec%22%2C%22subtitle_text_color%22%3A%22%23707579%22%2C%22destructive_text_color%22%3A%22%23df3f40%22%7D")
    vadim = ("Vadim", "https://hamsterkombat.io/clicker#tgWebAppData=query_id%3DAAG_TO5fAAAAAL9M7l95GfNN%26user%3D%257B%2522id%2522%253A1609452735%252C%2522first_name%2522%253A%2522Vadim%2522%252C%2522last_name%2522%253A%2522Noodle%2522%252C%2522username%2522%253A%2522Vadim_noodle%2522%252C%2522language_code%2522%253A%2522ru%2522%252C%2522is_premium%2522%253Atrue%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1723906952%26hash%3D26844b1efa02bb307b68c1724f380e3a11caac9e3d436ab09f87712f53d3723a&amp;tgWebAppVersion=7.6&amp;tgWebAppPlatform=web&amp;tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%233390ec%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23707579%22%2C%22link_color%22%3A%22%2300488f%22%2C%22secondary_bg_color%22%3A%22%23f4f4f5%22%2C%22text_color%22%3A%22%23000000%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22accent_text_color%22%3A%22%233390ec%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%233390ec%22%2C%22subtitle_text_color%22%3A%22%23707579%22%2C%22destructive_text_color%22%3A%22%23df3f40%22%7D")
    users = [nasty, vadim]

    global_stop_event = threading.Event()
    threads = []
    try:
        for user in users:
            thread = threading.Thread(target=interact_with_page, args=(*user, global_stop_event), daemon=True)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except (KeyboardInterrupt, MaxRetryError, NewConnectionError):
        global_stop_event.set()
        logger.info("Прерывание программы. Завершение потоков...")

    finally:
        for thread in threads:
            thread.join()
        logger.info("Все потоки завершены.")
