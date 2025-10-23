"""Run main logic by calling the appropriate modules."""
import datetime
import logging
import os

from dotenv import load_dotenv

from autovisa import schedule
from autovisa.src import LOGGING_LEVEL
from autovisa.src.constants import LOGGER_NAME
from autovisa.src.utils import hibernate

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger('seleniumwire').setLevel(logging.ERROR)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(LOGGING_LEVEL)
    logger.debug("> main")

    applicant_info = os.getenv("APPLICANT_ID", "").strip().upper()
    while not applicant_info:
        applicant_info = input("Enter applicant's full name or passport: ").strip().upper()

    while True:
        logger.info("=" * 80)
        logger.info("/ Initiating new instance at %s", datetime.datetime.now())
        scheduler = schedule.Scheduler()
        try:
            scheduler.run_reschedule_suite(applicant_info=applicant_info)
        except Exception as err:
            logger.error(str(err), exc_info=err)
        logger.info("... Hibernating at %s", datetime.datetime.now())
        hibernate()
