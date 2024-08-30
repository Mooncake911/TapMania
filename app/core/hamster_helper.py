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
    def __init__(self, name, src, platform, timeout, num_clicks, headless,
                 claim_daily_rewards, use_energy_boosts):
        super().__init__(headless=headless)
        self.stop_event = threading.Event()
        self.base_url = self.rewrite_html(name, src, platform)
        self.timeout = timeout
        self.num_clicks = num_clicks
        self.claim_daily_rewards = claim_daily_rewards
        self.use_energy_boosts = use_energy_boosts

        if self.base_url:
            self.driver.get(self.base_url)
            self.driver.set_window_rect(width=300, height=800)
        else:
            self.stop_event.set()
            logger.error(f'Для пользователя [{name}] неверно указан src: {src}')

    @staticmethod
    def check_stop_event(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            attempts = 0
            max_attempts = 3

            while attempts < max_attempts:
                try:
                    if self.stop_event.is_set():
                        break
                    else:
                        return func(self, *args, **kwargs)

                except (ElementClickInterceptedException, ElementNotInteractableException):
                    try:
                        try:
                            self.popup_window_button_large(
                                massage=f"Появление всплывающего окна, возможно повысился уровень.")
                        except Exception as inner_e:
                            logger.warning(f"Не удалось нажать большую кнопку всплывающего окна: {inner_e}", exc_info=True)
                        try:
                            self.popup_window_button_close(
                                massage=f"Закрытие всплывающего окна, возможно повысился уровень.")
                        except Exception as inner_e:
                            logger.warning(f"Не удалось нажать кнопку закрытия всплывающего окна: {inner_e}", exc_info=True)
                    except Exception as outer_e:
                        logger.error(f"Проблема с прерыванием элемента не была решена.\n{outer_e}", exc_info=True)

                except (TimeoutException, StaleElementReferenceException):
                    attempts += 1
                    logger.warning(f"Что-то пошло не так: {attempts}-ая попытка найти элемент.", exc_info=True)

                except NoSuchElementException as e:
                    logger.warning(f"Элемент не был найден на странице.\n{e}", exc_info=True)

                except NoSuchWindowException:
                    logger.warning(f"Было закрыто окно браузера.")
                    break

                except (ConnectionError, WebDriverException):
                    attempts += 1
                    self.driver.refresh()
                    self.switch_to_iframe()
                    logger.warning(f"WebDriver был перезапущен {attempts} раз.")

                except StopIteration:
                    logger.info(f"Вызвана остановка программы.")
                    break

                except KeyboardInterrupt:
                    logger.warning(f"Было принудительное прерывание программы или закрытие окна.")
                    break

                except Exception as e:
                    logger.error(f"Неизвестная ошибка.\n{e}", exc_info=True)
                    break

            self.close()

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
    def scroll_page(driver):
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

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

        time.sleep(2)
        driver.execute_script(script)
        time.sleep(2)

    @check_stop_event
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

    def popup_window_button_large(self, massage):
        """ Всплывающее окно. """
        try:
            large_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'bottom-sheet-button.button.button-primary.button-large'))
            )
            large_button.click()
            logger.info(massage)
        except (TimeoutException, StaleElementReferenceException,
                ElementClickInterceptedException, ElementNotInteractableException):
            pass

    def popup_window_button_close(self, massage):
        """ Закрытие всплывающего окна. """
        try:
            close_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'bottom-sheet-close'))
            )
            close_button.click()
            logger.info(massage)
        except (TimeoutException, StaleElementReferenceException,
                ElementClickInterceptedException, ElementNotInteractableException):
            pass

    @check_stop_event
    def app_bar_items(self, index, massage):
        """ Переход на элемент в нижнем меню. """
        self.scroll_page(self.driver)

        bar_buttons = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.app-bar-item.no-select'))
        )
        bar_buttons[index].click()

        logger.info(massage)

    @check_stop_event
    def use_boosts(self):
        """ Используем бустеры энергии если они есть. """
        try:
            self.scroll_page(self.driver)
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

        except (TimeoutException,  ElementClickInterceptedException):
            self.app_bar_items(index=0, massage=f"Переход на главную страницу.")
            logger.info(f"Нет доступного бустера энергии.")
            return False

    @check_stop_event
    def tap_tap(self):
        """ Начать нажимать по кнопке. """
        self.scroll_page(self.driver)
        hamster_button = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'user-tap-button.button'))
        )

        for _ in range(self.num_clicks):
            # Начитаем нажимать на хомяка
            if not self.stop_event.is_set():
                try:
                    try:
                        hamster_button.click()
                    except (TimeoutException, ElementClickInterceptedException):
                        self.scroll_page(self.driver)
                        hamster_button.click()
                    time.sleep(random.randint(1, 10) / 100)
                except ElementNotInteractableException:
                    logger.warning(f"Не удалось нажать на хомяка.")
                    continue
            else:
                raise StopIteration

        if self.use_boosts():
            self.tap_tap()

    @check_stop_event
    def claim_rewards(self):
        """ Собрать монеты со всех ежедневных активностей. """
        self.app_bar_items(index=4, massage=f"Переход на страницу ежедневных активностей.")

        self.block_sites(driver=self.driver,
                         blocked_urls=["youtu.be", "youtube.com",
                                       "facebook.com",
                                       "instagram.com",
                                       "twitter.com", "x.com"])

        self.scroll_page(self.driver)
        earn_column = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, 'earn-column'))
        )

        for column in earn_column:
            # Получаем элементы содержащиеся в колонке
            if not self.stop_event.is_set():
                earn_items = WebDriverWait(column, self.timeout).until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, 'earn-item'))
                )
            else:
                raise StopIteration

            for item in earn_items:
                # Проходимся по всем элементам в колонке
                if not self.stop_event.is_set():
                    try:
                        try:
                            item.click()
                        except (TimeoutException, ElementClickInterceptedException):
                            self.scroll_page(self.driver)
                            item.click()
                    except ElementNotInteractableException:
                        logger.warning(f"Задание не выполнено.")
                        continue

                    self.popup_window_button_large(massage=f"Задание выполнено.")
                    self.popup_window_button_close(massage=f"Задание выполнено.")
                else:
                    raise StopIteration

        self.app_bar_items(index=0, massage=f"Переход на главную страницу.")

    @check_stop_event
    def play_morse(self):
        """ Пройти ежедневную игру Морзе. """
        pass

    @check_stop_event
    def get_energy(self):
        """ Получаем текущие значения энергии. """
        self.scroll_page(self.driver)

        max_attempts = 5
        attempts = 0

        while attempts < max_attempts:
            try:
                energy_limit_element = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.user-tap-energy p'))
                )
                energy_limit_text = energy_limit_element.text.strip()

                if '/' in energy_limit_text:
                    current_energy_balance, max_energy_limit = energy_limit_text.split('/')
                    current_energy_balance = int(current_energy_balance.strip())
                    max_energy_limit = int(max_energy_limit.strip())
                    return current_energy_balance, max_energy_limit
                else:
                    break

            except ElementNotInteractableException:
                self.scroll_page(self.driver)

            except TypeError:
                attempts += 1

        return 0, 1000

    def start(self):
        """ Начать добывать монеты пока не будет установлено событие остановки. """
        attempts = 0
        max_attempts = 1000

        end_time = 0

        self.switch_to_iframe()
        self.popup_window_button_large(massage=f"Биржа принесла доход.")

        while attempts < max_attempts:
            try:
                if self.stop_event.is_set():
                    break

                else:
                    if time.time() > end_time:
                        end_time = time.time() + 12 * 60 * 60
                        if self.claim_daily_rewards:
                            self.claim_rewards()
                            logger.info(f"Ежедневные награды были собраны.")

                    current_energy_balance, max_energy_limit = self.get_energy()
                    logger.info(f"Текущий баланс энергии: {current_energy_balance}")

                    if (max_energy_limit - current_energy_balance) < max_energy_limit * 0.25:
                        logger.info(f"Добыча монет в Hamster Kombat запущена.")
                        self.tap_tap()
                        logger.info(f"Добыча монет Hamster Kombat завершёна.")

                    else:
                        wait_time = (max_energy_limit - current_energy_balance) * (30 / 100)  # 100 за 30 сек
                        logger.info(f"Ожидание заполнения энергии: {wait_time / 60} мин.")
                        end_time = time.time() + wait_time
                        while time.time() < end_time:
                            if self.stop_event.is_set():
                                break
                            time.sleep(0.1)

            except StopIteration:
                break

            except Exception as e:
                logger.error(f"Поймана ошибка: {e}", exc_info=True)

        self.close()

    def stop(self):
        self.stop_event.set()


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
