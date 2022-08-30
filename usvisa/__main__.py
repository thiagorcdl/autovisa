#!/usr/bin/env python
"""Run main logic by calling the appropriate modules."""

import logging
from usvisa import schedule

logger = logging.getLogger()

if __name__ == "__main__":
    logger.debug("> main")
    scheduler = schedule.Scheduler()
    scheduler.reschedule_sooner()
