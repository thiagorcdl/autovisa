#!/usr/bin/env python
"""Run main logic by calling the appropriate modules."""

import logging
from usvisa import schedule

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    logger = logging.getLogger()

    logger.debug("> main")
    scheduler = schedule.Scheduler()
    scheduler.reschedule_sooner()
