"""Hold default values."""
import logging
from selenium import webdriver

LOGGING_LEVEL = logging.INFO

MIN_ACTION_SLEEP = 1
MAX_ACTION_SLEEP = 4

LOGIN_URL = "https://ais.usvisa-info.com/en-ca/niv/users/sign_in"

DEFAULT_WEBDRIVER = webdriver.Firefox
