"""Provide scheduling utility scripts."""

import logging

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from usvisa.src.constants import DEFAULT_WEBDRIVER

logger = logging.getLogger()


class Scheduler:

    def __init__(self):
        self.driver = DEFAULT_WEBDRIVER()

    def navigate_login_page(self):
        # TODO implement
        return

    def execute_login(self):
        # TODO implement
        return

    def get_current_appointment(self):
        # TODO implement
        return

    def navigate_reschedule_page(self):
        # TODO implement
        return

    def get_best_date(self):
        # TODO implement
        return

    def execute_reschedule(self):
        # TODO implement
        return

    def reschedule_sooner(self):
        logger.debug("> reschedule_sooner")
        self.navigate_login_page()
        self.execute_login()
        self.get_current_appointment()
        self.navigate_reschedule_page()
        self.get_best_date()
        self.execute_reschedule()
        return
