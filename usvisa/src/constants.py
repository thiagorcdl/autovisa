"""Hold default values."""
import logging
from selenium import webdriver

LOGGING_LEVEL = logging.INFO

MIN_ACTION_SLEEP = 1
MAX_ACTION_SLEEP = 4

LOGIN_URL = "https://ais.usvisa-info.com/en-ca/niv/users/sign_in"

DEFAULT_WEBDRIVER_CLASS = webdriver.Chrome

DEFAULT_USERAGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/104.0.5112.102 Safari/537.36"
)
