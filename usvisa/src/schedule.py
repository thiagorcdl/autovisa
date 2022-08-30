"""Provide scheduling utility scripts."""

import logging

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from usvisa.src.constants import DEFAULT_WEBDRIVER, LOGIN_URL

logger = logging.getLogger()


class Appointment:
    city = None
    date = None
    time = None


class Scheduler:

    driver = None
    current_appointment: Appointment = None
    new_appointment: Appointment = None

    def __init__(self):
        self.driver = DEFAULT_WEBDRIVER()

    def navigate_login_page(self):
        self.driver.get(LOGIN_URL)
        return

    def execute_login(self):
        # Find email field
        # Fill in email field
        # Find pwd field
        # Fill in pwd field
        # Find CTA
        # Click CTA
        return

    def get_current_appointment(self):
        # Find appointment element
        # Retrieve text
        # Parse text
        # Store in attribute
        return

    def navigate_reschedule_page(self):
        # Find "continue" CTA
        # Click CTA
        # Find "reschedule" section
        # Expand "reschedule" section
        # Find "reschedule" CTA
        # Click CTA
        return

    def get_best_date(self):
        # Find dropdown of cities
        # For each city
            # Select city
            # TODO find out if possible: get json results
            # get first date
            # compare with self.current_appointment
            # set self.new_appointment
        return self.new_appointment

    def execute_reschedule(self):
        # Find dropdown of cities
        # Select self.new_appointment.city
        # Find date field
        # Find calendar
        return

    def reschedule_sooner(self):
        logger.debug("> reschedule_sooner")
        self.navigate_login_page()
        self.execute_login()
        self.get_current_appointment()
        self.navigate_reschedule_page()
        self.get_best_date()
        if self.new_appointment.date < self.current_appointment:
            self.execute_reschedule()
        return
