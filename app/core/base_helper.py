from logging_config import logger

import sys
from selenium.common.exceptions import WebDriverException


from .my_driver import get_web_driver


class BaseHelper(object):
    def __init__(self, headless):
        self.driver = get_web_driver(headless=headless)
        logger.info(f"WebDriver has been successfully initialized.")

    def close(self):
        """ Остановка Webdriver. """
        try:
            if self.driver:
                self.driver.close()
                self.driver.quit()
                logger.info(f"WebDriver has been stopped.")

        except WebDriverException:
            logger.info(f"The browser window was closed before WebDriver was stopped.")

        finally:
            sys.exit(0)
