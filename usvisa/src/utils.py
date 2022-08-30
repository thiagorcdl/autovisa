"""Utility functions."""
import os
import random
import time
from functools import lru_cache
from usvisa.src.constants import MAX_ACTION_SLEEP, MIN_ACTION_SLEEP


def delayed(function):
    """Decorate function to add a random delay before taking action."""

    def wrapper(*args, **kwargs):
        """Add delay and execute wrapped function."""
        rand_sleep()
        return function(*args, **kwargs)

    return wrapper


def rand_sleep():
    """Set execution to halt for a random amount of time."""
    sleep_duration = random.randint(MIN_ACTION_SLEEP, MAX_ACTION_SLEEP)
    time.sleep(sleep_duration)


@lru_cache
def get_credentials() -> tuple:
    """Retrieve login and password from environment variables."""
    login = os.environ.get("USVISA_LOGIN")
    pwd = os.environ.get("USVISA_PWD")
    return login, pwd
