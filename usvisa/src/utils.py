"""Utility functions."""
import os
import random
import time
from functools import lru_cache
from usvisa.src.constants import MAX_ACTION_SLEEP, MIN_ACTION_SLEEP


def delayed(function, *args):
    """Decorate function to add a random delay before taking action."""
    args_map = {
        "normal": rand_sleep,
        "quick": quick,
        "slow": quick,
        "hibernate": quick,
    }

    arg = args[0] if args else None
    sleep_function = args_map.get(arg, rand_sleep)

    def wrapper(*args, **kwargs):
        """Add delay and execute wrapped function."""
        sleep_function()
        return function(*args, **kwargs)

    return wrapper


def rand_sleep(min_sleep=MIN_ACTION_SLEEP, max_sleep=MAX_ACTION_SLEEP):
    """Set execution to halt for a random amount of time, in seconds."""
    max_sleep = max(0, max_sleep - 1)
    if max_sleep == 0:
        return

    sleep_duration = float(random.randint(min_sleep, max_sleep))
    sleep_duration += random.random()  # Add decimal to prevent always integer delays
    time.sleep(sleep_duration)


def quick():
    """Sleep a really small amount of time, no more than 1 second."""
    return rand_sleep(min_sleep=0, max_sleep=1)


def slow():
    """Sleep for some time, more than 3 seconds."""
    return rand_sleep(min_sleep=3, max_sleep=6)


def hibernate():
    """Sleep for a very long time, more than 2 minutes."""
    return rand_sleep(min_sleep=60*2, max_sleep=60*3)


@lru_cache
def get_credentials() -> tuple:
    """Retrieve login and password from environment variables."""
    login = os.environ.get("USVISA_LOGIN")
    pwd = os.environ.get("USVISA_PWD")
    return login, pwd
