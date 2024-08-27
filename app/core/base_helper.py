from logging_config import logger

import sys
from functools import wraps

from selenium.common.exceptions import (NoSuchElementException,
                                        ElementNotInteractableException,
                                        ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        TimeoutException,
                                        NoSuchWindowException,
                                        WebDriverException)

from urllib3.exceptions import ProtocolError, NewConnectionError, MaxRetryError


from .my_driver import get_web_driver


class BaseHelper(object):
    def __init__(self, headless):
        self.driver = get_web_driver(headless=headless)
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

    @handle_exceptions
    def close(self):
        """ Остановка Webdriver. """
        if self.driver:
            self.driver.close()
            self.driver.quit()

        logger.info(f"Chrome driver был остановлен.")
