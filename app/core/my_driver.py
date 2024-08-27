from logging_config import logger

import os
import platform
import subprocess

from selenium import webdriver


class BrowserNotFoundError(Exception):
    """ Custom exception when no one compatible browser is found. """
    pass


def get_browser_path(browser_name):
    os_type = platform.system()

    if os_type == "Windows":
        paths = {
            "chrome": [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ],
            "firefox": [
                "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
            ],
            "edge": [
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
            ],
            "brave": [
                "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
            ],
            "yandex": [
                "C:\\Program Files (x86)\\Yandex\\YandexBrowser\\browser.exe",
                "C:\\Program Files\\Yandex\\YandexBrowser\\browser.exe"
            ],
            "vivaldi": [
                "C:\\Program Files\\Vivaldi\\Application\\vivaldi.exe",
                "C:\\Program Files (x86)\\Vivaldi\\Application\\vivaldi.exe"
            ],
            "ie": [
                "C:\\Program Files\\Internet Explorer\\iexplore.exe",
                "C:\\Program Files (x86)\\Internet Explorer\\iexplore.exe"
            ],
        }
        for path in paths.get(browser_name, []):
            if os.path.exists(path):
                return True

    elif os_type == "Darwin":
        paths = {
            "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
            "edge": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "brave": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "yandex": "/Applications/Yandex.app/Contents/MacOS/Yandex",
            "vivaldi": "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi",
        }
        return os.path.exists(paths.get(browser_name, ""))

    elif os_type == "Linux":
        commands = {
            "chrome": "google-chrome --version",
            "firefox": "firefox --version",
            "edge": "microsoft-edge --version",
            "brave": "brave --version",
            "yandex": "yandex-browser --version",
            "vivaldi": "vivaldi --version",
        }
        command = commands.get(browser_name)
        if command:
            try:
                subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                return True
            except subprocess.CalledProcessError:
                return False

    return False


def setup_webdriver(browser_name, headless):
    if browser_name in ["chrome", "brave", "yandex", "vivaldi"]:
        service = webdriver.ChromeService()
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless=old')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--log-level=3')
        return webdriver.Chrome(service=service, options=options)

    elif browser_name == "edge":
        service = webdriver.EdgeService()
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument('--headless=old')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--log-level=3')
        return webdriver.Edge(service=service, options=options)

    elif browser_name == "firefox":
        service = webdriver.FirefoxService()
        options = webdriver.FirefoxOptions()
        options.headless = headless
        return webdriver.Firefox(service=service, options=options)

    elif browser_name == "ie":
        service = webdriver.IeService()
        options = webdriver.IeOptions()
        options.headless = headless
        return webdriver.Firefox(service=service, options=options)

    raise BrowserNotFoundError(f"No suitable WebDriver found for browser: {browser_name}")


def get_web_driver(headless=True):
    browsers = ["chrome", "edge", "firefox", "yandex", "brave", "vivaldi", "ie"]
    for browser in browsers:
        if get_browser_path(browser):
            return setup_webdriver(browser, headless)
    raise BrowserNotFoundError("No compatible browsers are installed.")
