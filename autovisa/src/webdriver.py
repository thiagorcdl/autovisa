import logging
import random
import typing as t

import seleniumwire
from selenium import webdriver
from selenium.common import ElementNotInteractableException, NoSuchElementException
from seleniumwire import undetected_chromedriver
from seleniumwire.undetected_chromedriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement

from autovisa.src.constants import (
    BY_TYPE_ORDER,
    DEFAULT_WEBDRIVER_CLASS
)
from autovisa.src.utils import (
    delayed, get_user_agent,
    quick_delayed, quick_sleep
)

logger = logging.getLogger()


class WebDriver:
    _WEBDRIVER_CLASS = DEFAULT_WEBDRIVER_CLASS
    driver = None

    def __init__(self):
        driver_args, driver_kwargs = self.get_driver_args()
        self.driver = DEFAULT_WEBDRIVER_CLASS(*driver_args, **driver_kwargs)

    def get_driver_args(self) -> tuple:
        """Return arguments for instantiating driver."""
        driver_args = []
        driver_kwargs = {}
        user_agent = get_user_agent()

        if self._WEBDRIVER_CLASS in (webdriver.Chrome, seleniumwire.webdriver.Chrome):
            options = Options()
            options.add_argument(f"user-agent={user_agent}")
            options.add_argument('--ignore-ssl-errors=yes')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-insecure-localhost')
            driver_kwargs["chrome_options"] = options
        elif self._WEBDRIVER_CLASS == undetected_chromedriver.Chrome:
            options = ChromeOptions()
            options.add_argument(f"user-agent={user_agent}")
            options.add_argument('--ignore-ssl-errors=yes')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-insecure-localhost')
            driver_kwargs["options"] = options
            driver_kwargs["version_main"] = 122
        elif self._WEBDRIVER_CLASS == webdriver.Firefox:
            profile = webdriver.FirefoxProfile()
            profile.set_preference("general.user_agent.override", user_agent)
            driver_args.append(profile)

        return driver_args, driver_kwargs

    def find_element(self, by_type, key: str) -> WebElement:
        """Find element via defined "by" type."""
        logger.debug("> find_element")
        try:
            return self.driver.find_element(by_type, key)
        except NoSuchElementException as err:
            pass

    def instant_select_element(self, key: str) -> t.Optional[WebElement]:
        """Find and click element."""
        logger.debug("> select_element")
        for by_type in BY_TYPE_ORDER:
            element = self.find_element(by_type, key)

            if not element:
                continue

            try:
                element.click()
            except ElementNotInteractableException:
                return None
            return element

    @delayed
    def slow_select_element(self, key: str) -> t.Optional[WebElement]:
        """Find and click element."""
        return self.instant_select_element(key)

    @quick_delayed
    def quick_select_element(self, key: str) -> t.Optional[WebElement]:
        """Find and click element."""
        return self.instant_select_element(key)

    def select_random_element(self, selector_choices) -> t.Optional[WebElement]:
        """Run select_element() with a randomly-chosen selector."""
        selector = random.choice(selector_choices)
        return self.slow_select_element(selector)

    @delayed
    def write_input(self, element: WebElement, text: str):
        """Send text to input element, character by character."""
        logger.debug("> write_input")

        for char in text:
            quick_sleep()
            element.send_keys(char)
