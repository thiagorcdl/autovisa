import logging
import random
import typing as t
from pathlib import Path

import seleniumwire
from selenium import webdriver
from selenium.common import ElementNotInteractableException, NoSuchElementException, \
    InvalidSelectorException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire import undetected_chromedriver
from seleniumwire.undetected_chromedriver import ChromeOptions

from autovisa.src.constants import (
    BY_TYPE_ORDER,
    DEFAULT_WEBDRIVER_CLASS, LOGGER_NAME, MAX_CLICK_ATTEMPTS
)
from autovisa.src.utils import (
    delayed, get_user_agent,
    quick_delayed, quick_sleep
)

logger = logging.getLogger(LOGGER_NAME)

# Project-local, pinned Chrome install used to actually drive the site,
# populated by scripts/install_chrome.sh.
# webdriver.py lives at <repo>/autovisa/src/webdriver.py
CHROME_DIR = Path(__file__).resolve().parents[2] / ".chrome"


def _find_local_binary(pattern: str) -> t.Optional[str]:
    """Return the first binary matching ``pattern`` under the local .chrome dir."""
    matches = sorted(CHROME_DIR.glob(pattern))
    return str(matches[0]) if matches else None


def get_local_chrome() -> t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]:
    """Locate the project-local Chrome browser, chromedriver and major version.

    Returns ``(browser_path, driver_path, version_main)``. Elements are ``None``
    when the artifact is missing; run ``scripts/install_chrome.sh`` to populate
    the ``.chrome`` directory with a matched browser/driver pair.
    """
    browser = _find_local_binary("chrome-*/chrome")
    driver = _find_local_binary("chromedriver-*/chromedriver")

    version_main = None
    version_file = CHROME_DIR / "VERSION"
    if version_file.exists():
        try:
            version_main = int(version_file.read_text().strip().split(".")[0])
        except ValueError:
            version_main = None

    return browser, driver, version_main


class WebDriver:
    _WEBDRIVER_CLASS = DEFAULT_WEBDRIVER_CLASS
    driver = None

    def __init__(self):
        driver_args, driver_kwargs = self.get_driver_args()
        self.driver = DEFAULT_WEBDRIVER_CLASS(*driver_args, **driver_kwargs)
        self.driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})

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

            browser_path, driver_path, version_main = get_local_chrome()
            if not browser_path or not driver_path:
                raise FileNotFoundError(
                    "Project-local Chrome not found in "
                    f"'{CHROME_DIR}'. Run scripts/install_chrome.sh to download "
                    "a matched Chrome browser and chromedriver."
                )
            options.binary_location = browser_path
            driver_kwargs["browser_executable_path"] = browser_path
            driver_kwargs["driver_executable_path"] = driver_path
            if version_main is not None:
                driver_kwargs["version_main"] = version_main
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
        except (NoSuchElementException, InvalidSelectorException) as err:
            pass

    def instant_select_element(self, key: str, attempt: int = 1) -> t.Optional[WebElement]:
        """Find and click element."""
        if attempt > MAX_CLICK_ATTEMPTS:
            return None

        logger.debug("> select_element" + f"(attempt #{attempt})" if attempt > 1 else "")
        for by_type in BY_TYPE_ORDER:
            element = self.find_element(by_type, key)

            if not element:
                continue

            try:
                element.click()
            except StaleElementReferenceException:
                return self.instant_select_element(key, attempt + 1)
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
