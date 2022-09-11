"""Store default values."""
import datetime
import logging

from selenium.webdriver.common.by import By
from seleniumwire import undetected_chromedriver

LOGGING_LEVEL = logging.INFO

MIN_ACTION_SLEEP = 1
MAX_ACTION_SLEEP = 2

LOGIN_URL = "https://ais.usvisa-info.com/en-ca/niv/users/sign_in"

DEFAULT_WEBDRIVER_CLASS = undetected_chromedriver.Chrome

DEFAULT_USERAGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/104.0.5112.102 Safari/537.36"
)

BY_TYPE_ORDER = (
    By.ID, By.CSS_SELECTOR, By.XPATH, By.NAME, By.CLASS_NAME, By.LINK_TEXT, By.TAG_NAME
)

CITY_NAME_ID_MAP = {
    "Calgary": "89",
    "Halifax": "90",
    "Montreal": "91",
    "Ottawa": "92",
    "Quebec City": "93",
    "Toronto": "94",
    "Vancouver": "95",
}

MAX_REQUEST_SEARCHES = 2

EXCLUDE_DATE_START = datetime.date(2022, 11, 15)
EXCLUDE_DATE_END = datetime.date(2022, 12, 1)

# --- Constants for testing --- #

TEST_LOGIN = "jerrymtc98@hotmail.com"
TEST_PWD = "qwerty1234qwerty"

TEST_USERAGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/51.0.2704.103 Safari/537.36"
)
