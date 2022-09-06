"""Provide scheduling utility scripts."""
import datetime
import logging
import re

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from seleniumwire import undetected_chromedriver
from seleniumwire.undetected_chromedriver import ChromeOptions

from usvisa.src.constants import (
    BY_TYPE_ORDER, DEFAULT_USERAGENT,
    DEFAULT_WEBDRIVER_CLASS, LOGIN_URL
)
from usvisa.src.utils import (
    delayed, get_credentials, get_month_int, get_user_agent, hibernate,
    quick_sleep, wait_page_load
)

logger = logging.getLogger()


class Appointment:
    city = None
    date = None
    time = None

    def __init__(self, day, month, year, time, city):
        self.city = city
        self.date = datetime.date(year, month, day)
        self.time = time

    def __repr__(self):
        return f"{self.date_repr} {self.time} in {self.city}"

    @property
    def date_repr(self):
        """Return formatted date."""
        return self.date.strftime("%Y-%m-%d")


class Scheduler:

    _WEBDRIVER_CLASS = DEFAULT_WEBDRIVER_CLASS
    driver = None
    current_appointment: Appointment = None
    new_appointment: Appointment = None

    def __init__(self):
        driver_args, driver_kwargs = self.get_driver_args()
        self.driver = DEFAULT_WEBDRIVER_CLASS(*driver_args, **driver_kwargs)
        self.driver.scopes = ["*.json"]

    def get_driver_args(self) -> tuple:
        """Return arguments for instantiating driver."""
        driver_args = []
        driver_kwargs = {}
        user_agent = get_user_agent()

        if self._WEBDRIVER_CLASS == webdriver.Chrome:
            options = Options()
            options.add_argument(f"user-agent={user_agent}")
            driver_kwargs["chrome_options"] = options
        elif self._WEBDRIVER_CLASS == undetected_chromedriver.Chrome:
            options = ChromeOptions()
            options.add_argument(f"user-agent={user_agent}")
            driver_kwargs["options"] = options
            driver_kwargs["seleniumwire_options"] = {}
        elif self._WEBDRIVER_CLASS == webdriver.Firefox:
            profile = webdriver.FirefoxProfile()
            profile.set_preference("general.user_agent.override", user_agent)
            driver_args.append(profile)

        return driver_args, driver_kwargs

    def navigate_login_page(self):
        self.driver.get(LOGIN_URL)

    @delayed
    def select_element(self, key: str) -> WebElement:
        """Find and click element."""
        logger.debug(f"> select_element")
        for by_type in BY_TYPE_ORDER:
            try:
                element = self.driver.find_element(by_type, key)
            except NoSuchElementException:
                continue

            element.click()
            return element

    @delayed
    def write_input(self, element: WebElement, text: str):
        """Send text to input element, character by character."""
        logger.debug(f"> write_input")

        for char in text:
            quick_sleep()
            element.send_keys(char)

    def execute_login(self):
        email, password = get_credentials()

        # Find email field
        email_input = self.select_element("user_email")
        # Fill in email field
        self.write_input(email_input, email)

        # Find pwd field
        password_input = self.select_element("user_password")
        # Fill in pwd field
        self.write_input(password_input, password)

        # Consent to privacy policy
        self.select_element(".icheckbox")

        # Click CTA
        self.select_element("commit")

    def get_current_appointment(self):
        # Find appointment element
        text_wrapper = self.driver.find_element(By.CSS_SELECTOR, ".consular-appt")
        # Retrieve text
        day, month_name, year, time, city = re.findall(
            r"(\d+) ([a-zA-Z]+), (\d+), (\d\d:\d\d) ([a-zA-Z]+)",
            text_wrapper.text
        )[0]
        # Parse text
        month = get_month_int(month_name)
        # Store in attribute
        self.current_appointment = Appointment(int(day), month, int(year), time, city)

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
        hibernate()
        if self.new_appointment.date < self.current_appointment.date:
            self.execute_reschedule()
        return
