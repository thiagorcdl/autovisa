"""Provide scheduling utility scripts."""
import datetime
import logging
import re

import seleniumwire
from selenium import webdriver
from selenium.common import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

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
    delayed, get_credentials, get_month_int, get_dict_response, get_user_agent,
    hibernate,
    quick_sleep, wait_page_load, wait_request
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

    def get_driver_args(self) -> tuple:
        """Return arguments for instantiating driver."""
        driver_args = []
        driver_kwargs = {}
        user_agent = get_user_agent()

        if self._WEBDRIVER_CLASS in (webdriver.Chrome, seleniumwire.webdriver.Chrome):
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

    def find_element(self, by_type, key: str) -> WebElement:
        """Find element via defined "by" type."""
        logger.debug(f"> find_element")
        try:
            return self.driver.find_element(by_type, key)
        except NoSuchElementException as err:
            pass

    @delayed
    def select_element(self, key: str) -> WebElement:
        """Find and click element."""
        logger.debug(f"> select_element")
        for by_type in BY_TYPE_ORDER:
            element = self.find_element(by_type, key)

            if not element:
                continue

            try:
                element.click()
            except ElementNotInteractableException:
                return None
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
        logger.info(f"Current appointment: {self.current_appointment}")

    def navigate_reschedule_page(self):
        # Click "continue" CTA
        self.select_element(
            "div.application:nth-child(1) > div:nth-child(1) > div:nth-child(2) "
            "> ul:nth-child(1) > li:nth-child(1) > a:nth-child(1)"
        )
        # Wait for redirection
        wait_page_load()

        # Expand "reschedule" section
        self.select_element("li.accordion-item:nth-child(4) > a:nth-child(1)")
        # Click "reschedule" CTA
        self.select_element(
            "li.accordion-item:nth-child(4) > div:nth-child(2) > div:nth-child(1) "
            "> div:nth-child(2) > p:nth-child(2) > a:nth-child(1)"
        )
        # Wait for redirection
        wait_page_load()

    def get_best_date(self):
        # Find dropdown of cities
        city_select = Select(
            self.select_element("appointments_consulate_appointment_facility_id")
        )
        new_best_date = None
        for option in city_select.options:
            del self.driver.requests

            city_select.select_by_value(option.get_attribute("value"))
            date_select = self.select_element("appointments_consulate_appointment_date")
            if not date_select:
                # No dates for selected city
                logger.info(f"No dates for {option.text}")
                continue

            wait_request()
            request = self.driver.requests[0]
            i = 0
            count = 0
            error = False
            while ".json" not in request.path:
                i += 1
                if i >= len(self.driver.requests):
                    wait_request()
                    i = 0
                    count += 1

                    if count > 2:
                        logger.error(f"JSON request not found for {option.text}")
                        error = True
                        break

                request = self.driver.requests[i]

            if error:
                continue

            # get first date
            response = get_dict_response(request)
            first_date_repr = response[0]["date"]

            year, month, day = list(map(int, first_date_repr.split("-")))
            first_date = datetime.date(year, month, day)

            # TODO: uncomment
            # if first_date >= self.current_appointment.date:
            #     logger.info(f"Best date for {option.text} ignored: {first_date_repr} (later than existing appointment)")
            #     continue
            if new_best_date and first_date >= new_best_date:
                logger.info(f"Best date for {option.text} ignored: {first_date_repr} (later than new best date)")
                continue
            else:
                new_best_date = first_date
            self.new_appointment = Appointment(day, month, year, "", option.text)

        # TODO: Select best city again

        # Select date in calendar

        return self.new_appointment

    def execute_reschedule(self):
        # TODO: Find dropdown of cities
        # TODO: Select self.new_appointment.city
        # Select best date
        free_date_cell_key = ".ui-state-default[href]"
        free_date_cell = self.find_element(By.CSS_SELECTOR, free_date_cell_key)

        while not free_date_cell:
            self.select_element(".ui-datepicker-next")
            free_date_cell = self.find_element(By.CSS_SELECTOR, free_date_cell_key)

        quick_sleep()
        free_date_cell.click()
        return

    def reschedule_sooner(self):
        logger.debug("> reschedule_sooner")
        self.navigate_login_page()
        self.execute_login()
        self.get_current_appointment()
        self.navigate_reschedule_page()
        self.get_best_date()
        hibernate()
        if self.new_appointment:
            self.execute_reschedule()
        return
