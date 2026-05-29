"""Store default values."""
import logging

from selenium.webdriver.common.by import By
from seleniumwire import undetected_chromedriver

LOGGING_LEVEL = logging.INFO
LOGGER_NAME = "autovisa"

FALSY_STRINGS = ["", "0", "false", "no"]

MIN_ACTION_SLEEP = 1
MAX_ACTION_SLEEP = 2

LOGIN_PATH = "/en-ca/niv/users/sign_in"

DEFAULT_WEBDRIVER_CLASS = undetected_chromedriver.Chrome

DEFAULT_USERAGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/104.0.5112.102 Safari/537.36"
)

BY_TYPE_ORDER = (
    By.ID, By.CSS_SELECTOR, By.XPATH, By.NAME, By.CLASS_NAME, By.LINK_TEXT, By.TAG_NAME
)

# Maps the user-facing slug to its facility ID.
CITY_SLUG_ID_MAP = {
    "calgary": "89",
    "halifax": "90",
    "montreal": "91",
    "ottawa": "92",
    "quebec-city": "93",
    "toronto": "94",
    "vancouver": "95",
}

# Open extremes used to fill in whichever bound the user omits, so a single
# bound yields an open-ended exclusion window.
DEFAULT_EXCLUDE_DATE_START = "1970-01-01"
DEFAULT_EXCLUDE_DATE_END = "2999-12-31"  # TODO fix this before year 3000

MAX_REQUEST_SEARCHES = 2
MAX_CLICK_ATTEMPTS = 3

# --- Constants for testing --- #

TEST_LOGIN = "jerrymtc98@hotmail.com"
TEST_PWD = "qwerty1234qwerty"

TEST_USERAGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/51.0.2704.103 Safari/537.36"
)
