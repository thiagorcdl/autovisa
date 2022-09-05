"""Hold default values."""
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By

LOGGING_LEVEL = logging.INFO

MIN_ACTION_SLEEP = 1
MAX_ACTION_SLEEP = 4

LOGIN_URL = "https://ais.usvisa-info.com/en-ca/niv/users/sign_in"

DEFAULT_WEBDRIVER_CLASS = webdriver.Firefox

DEFAULT_USERAGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/104.0.5112.102 Safari/537.36"
)

BY_TYPE_ORDER = (
    By.ID, By.CSS_SELECTOR, By.XPATH, By.NAME, By.CLASS_NAME, By.LINK_TEXT, By.TAG_NAME
)

# Test cosntants

TEST_LOGIN = "jerrymtc98@hotmail.com"
TEST_PWD = "qwerty1234qwerty"

TEST_USERAGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/51.0.2704.103 Safari/537.36"
)
