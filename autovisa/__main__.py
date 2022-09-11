"""Run main logic by calling the appropriate modules."""
import datetime
import logging
from autovisa import schedule
from autovisa.src import LOGGING_LEVEL
from autovisa.src.utils import hibernate

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(LOGGING_LEVEL)
    logger = logging.getLogger()
    logging.getLogger('seleniumwire').setLevel(logging.ERROR)
    logger.debug("> main")

    while True:
        logger.info("=" * 80)
        logger.info("Initiating new instance at %s", datetime.datetime.now())
        scheduler = schedule.Scheduler()
        try:
            scheduler.reschedule_sooner()
        except Exception as err:
            logger.error(str(err), exc_info=err)
        hibernate()
