"""Utility functions."""
import logging
import os
import random
import time
from functools import lru_cache, wraps
from usvisa.src.constants import (
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


def rand_sleep(min_sleep=MIN_ACTION_SLEEP, max_sleep=MAX_ACTION_SLEEP):
    """Set execution to halt for a random amount of time, in seconds."""
    if max_sleep <= 0 or max_sleep <= min_sleep:
        return

    max_sleep = max(0, max_sleep - 1)

    sleep_duration = float(random.randint(min_sleep, max_sleep))
    sleep_duration += random.random()  # Add decimal to prevent always integer delays
    time.sleep(sleep_duration)


def quick_sleep():
    """Sleep a really small amount of time, no more than 1 second."""
    return rand_sleep(min_sleep=0, max_sleep=1)


def long_sleep():
    """Sleep for some time, more than 3 seconds."""
    return rand_sleep(min_sleep=3, max_sleep=6)


def hibernate():
    """Sleep for a very long time, more than 2 minutes."""
    return rand_sleep(min_sleep=60*2, max_sleep=60*3)


@lru_cache
def is_testing() -> bool:
    """Check whether current instance is for testing."""
    falsy_strings = ["0", "false", "no"]
    env_variable = os.environ.get("TEST")
    if env_variable.lower() in falsy_strings:
        return False

    return bool(env_variable)


@lru_cache
def get_credentials() -> tuple:
    """Retrieve login and password from environment variables."""
    if is_testing():
        login = TEST_LOGIN
        password = TEST_PWD
    else:
        login = os.environ.get("USVISA_LOGIN")
        password = os.environ.get("USVISA_PWD")

        if not login and password:
            raise ValueError("Missing credentials")

    return login, password


def get_user_agent() -> str:
    """Retrieve user agent string to be used in the webdriver."""
    return TEST_USERAGENT if is_testing() else DEFAULT_USERAGENT
