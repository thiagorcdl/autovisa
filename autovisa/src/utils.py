"""Utility functions."""
import calendar
import json
import logging
import os
import random
import time
from functools import lru_cache, wraps

from seleniumwire.request import Request
from seleniumwire.utils import decode

from autovisa.src.constants import (
    DEFAULT_USERAGENT, MAX_ACTION_SLEEP, MIN_ACTION_SLEEP,
    TEST_LOGIN, TEST_PWD, TEST_USERAGENT
)

logger = logging.getLogger()


def delayed(function):
    """Decorate function to add a random delay before taking action."""
    logger.debug(f">> delayed decorator")

    @wraps(function)
    def wrapper(*args, **kwargs):
        """Add delay and execute wrapped function."""
        logger.debug(f">>> delayed wrapper")
        rand_sleep()
        return function(*args, **kwargs)

    return wrapper


def quick_delayed(function):
    """Decorate function to add a quick delay before taking action."""
    logger.debug(f">> quick_delayed decorator")

    @wraps(function)
    def wrapper(*args, **kwargs):
        """Add delay and execute wrapped function."""
        logger.debug(f">>> quick_delayed wrapper")
        quick_sleep()
        return function(*args, **kwargs)

    return wrapper


def rand_sleep(min_sleep=MIN_ACTION_SLEEP, max_sleep=MAX_ACTION_SLEEP):
    """Set execution to halt for a random amount of time, in seconds."""
    if max_sleep <= 0 or max_sleep <= min_sleep:
        return

    max_sleep = max(0, max_sleep - 1)

    sleep_duration = float(random.randint(min_sleep, max_sleep))
    sleep_duration += random.random() / 2  # Add decimal to prevent always integer
    logger.debug("> sleeping for %f seconds", sleep_duration)
    time.sleep(sleep_duration)


def quick_sleep():
    """Sleep a really small amount of time, no more than 1 second."""
    return rand_sleep(min_sleep=0, max_sleep=1)


def long_sleep():
    """Sleep for some time, more than 10 seconds."""
    return rand_sleep(min_sleep=10, max_sleep=20)


def hibernate():
    """Sleep for a very long time, more than 5 minutes."""
    return rand_sleep(min_sleep=60 * 5, max_sleep=60 * 10)


def wait_page_load():
    """Sleep for enough time for the webdriver to execute the action and page to
    reload.
    """
    return time.sleep(2.5)


def wait_request():
    """Sleep for enough time for a single request."""
    return time.sleep(1)


def get_response_body(request: Request) -> bytes:
    """Esctract response body from request."""
    response = request.response
    return decode(
        response.body,
        response.headers.get('Content-Encoding', 'identity')
    )


def get_dict_response(request) -> list:
    """Parse JSON response as list."""
    response_body = get_response_body(request)
    return json.loads(response_body)


@lru_cache
def is_env(env_var_name: str) -> bool:
    """Check whether environment variable yields True."""
    falsy_strings = ["", "0", "false", "no"]
    value = os.environ.get(env_var_name, "")
    if value.lower() in falsy_strings:
        return False

    return bool(value)


@lru_cache
def is_prod() -> bool:
    """Check whether current instance is for production."""
    return is_env("PRODUCTION")


@lru_cache
def is_testing() -> bool:
    """Check whether current instance is for testing."""
    return is_env("TEST")


@lru_cache
def get_credentials() -> tuple:
    """Retrieve login and password from environment variables."""
    if is_testing():
        login = TEST_LOGIN
        password = TEST_PWD
    else:
        login = os.environ.get("VISA_EMAIL")
        password = os.environ.get("VISA_PASSWORD")

        if not login and password:
            raise ValueError("Missing credentials")

    return login, password


def get_user_agent() -> str:
    """Retrieve user agent string to be used in the webdriver."""
    return TEST_USERAGENT if is_testing() else DEFAULT_USERAGENT


def get_month_int(month_name: str) -> int:
    """Map a month name (title formatting) to an integer (0-indexed)."""
    return list(calendar.month_name).index(month_name.title())
