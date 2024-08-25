import sys

from pathlib import Path
from functools import wraps

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.common.exceptions import (NoSuchElementException,
                                        ElementNotInteractableException,
                                        ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        TimeoutException,
                                        NoSuchWindowException,
                                        WebDriverException)

from urllib3.exceptions import ProtocolError, NewConnectionError, MaxRetryError


from app.core.logging_config import logger


class BaseHelper(object):
    driver_path = Path('chromedriver-win64/chromedriver.exe')

    def __init__(self, show):
        options = Options()
        if not show:
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
                logger.error(f"Ошибка WebDriver.", exc_info=True)
                sys.exit(0)
            except (KeyboardInterrupt, ProtocolError, MaxRetryError, NewConnectionError):
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
