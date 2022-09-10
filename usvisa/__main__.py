
"""Run main logic by calling the appropriate modules."""

import logging
from usvisa import schedule
from usvisa.src import LOGGING_LEVEL

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(LOGGING_LEVEL)
    logger = logging.getLogger()

    logger.debug("> main")
    scheduler = schedule.Scheduler()
    scheduler.reschedule_sooner()
