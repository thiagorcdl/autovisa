"""Provide scheduling utility scripts."""
import datetime
import logging
import re
import typing as t

from selenium.webdriver import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from seleniumwire.request import Request

from usvisa.src.appointment import Appointment
from usvisa.src.constants import CITY_NAME_ID_MAP, MAX_REQUEST_SEARCHES

from usvisa.src.utils import (
    get_credentials, get_month_int, get_dict_response,
    is_prod, quick_sleep, wait_page_load, wait_request
)
from usvisa.src.webdriver import WebDriver

logger = logging.getLogger()


class Scheduler(WebDriver):
    """Class for encapsulating busines slogic for scheduling interviews."""
    current_appointment: t.Optional[Appointment] = None
    new_appointment: t.Optional[Appointment] = None

    def execute_login(self):
        """Fill in credentials, consent to privacy policity and try logging in."""
        email, password = get_credentials()

        email_input = self.select_element("user_email")
        self.write_input(email_input, email)

        password_input = self.select_element("user_password")
        self.write_input(password_input, password)

        # Consent to privacy policy
        self.select_element(".icheckbox")

        # Click CTA
        self.select_element("commit")

    def get_current_appointment(self):
        """Parse raw text in page and store new Appointment instance."""
        # Find appointment element
        text_wrapper = self.driver.find_element(By.CSS_SELECTOR, ".consular-appt")
        # Retrieve text
        day, month_name, year, time, city = re.findall(
            r"(\d+) ([a-zA-Z]+), (\d+), (\d\d:\d\d) ([a-zA-Z]+)",
            text_wrapper.text
        )[0]
        month = get_month_int(month_name)
        self.current_appointment = Appointment(int(day), month, int(year), time, city)
        logger.info("Current appointment: %s", self.current_appointment)

    def navigate_reschedule_page(self):
        """Expand appropriate section and click CTAs to open the rescheduling page."""
        # Click "continue" CTA
        self.select_element(
            "div.application:nth-child(1) > div:nth-child(1) > div:nth-child(2) "
            "> ul:nth-child(1) > li:nth-child(1) > a:nth-child(1)"
        )
        wait_page_load()

        # Expand "reschedule" section
        self.select_element("li.accordion-item:nth-child(4) > a:nth-child(1)")
        # Click "reschedule" CTA
        self.select_element(
            "li.accordion-item:nth-child(4) > div:nth-child(2) > div:nth-child(1) "
            "> div:nth-child(2) > p:nth-child(2) > a:nth-child(1)"
        )
        wait_page_load()

    def find_json_request(self, city) -> t.Optional[Request]:
        """Traverse requests list multiple times to find the JSON response,
        which contains the avaialble dates.
        """
        wait_request()
        request = self.driver.requests[0]
        i = 0
        search_count = 0
        while ".json" not in request.path:
            i += 1
            if i >= len(self.driver.requests):
                wait_request()
                i = 0
                search_count += 1

                if search_count > MAX_REQUEST_SEARCHES:
                    logger.error("JSON request not found for %s", city)
                    return

            request = self.driver.requests[i]
        return request

    def validate_candidate(
        self, new_best_date, candidate, candidate_repr, city
    ) -> bool:
        """Ensure candidate for new best date is sooner than the best ones so far."""
        if is_prod() and candidate >= self.current_appointment.date:
            logger.info(
                "Best date for %s ignored: %s (later than existing appointment)",
                city, candidate_repr
            )
            return False

        if new_best_date and candidate >= new_best_date:
            logger.info(
                "Best date for %s ignored: %s (later than new best date)",
                city, candidate_repr
            )
            return False
        return True

    def get_best_date(self):
        """Find the soonest available date among all cities."""
        self.new_appointment = None
        new_best_date = None

        city_select_element = self.select_element(
            "appointments_consulate_appointment_facility_id")
        city_select = Select(city_select_element)

        for option in city_select.options:
            if not option.text:
                continue

            # Set clean slate / in case of "continue", close the calendar
            city_select_element.send_keys(Keys.ESCAPE)
            del self.driver.requests

            city_select.select_by_value(option.get_attribute("value"))
            date_select = self.select_element(
                "appointments_consulate_appointment_date")
            if not date_select:
                # No dates for selected city
                logger.info("No dates for %s", option.text)
                continue

            wait_request()
            request = self.find_json_request(option.text)

            if not request:
                continue

            # Get first date
            response = get_dict_response(request)
            candidate_repr = response[0]["date"]

            year, month, day = list(map(int, candidate_repr.split("-")))
            candidate = datetime.date(year, month, day)
            if not self.validate_candidate(
                new_best_date, candidate, candidate_repr, option.text
            ):
                continue
            new_best_date = candidate
            self.new_appointment = Appointment(day, month, year, "", option.text)

            logger.info("New best date found: %s", self.new_appointment)

        return self.new_appointment

    def execute_reschedule(self):
        """Select the info for the best appointment found."""
        city_select = Select(
            self.select_element("appointments_consulate_appointment_facility_id")
        )
        city_select.select_by_value(CITY_NAME_ID_MAP[self.new_appointment.city])

        # Select soonest date in calendar
        self.select_element("appointments_consulate_appointment_date")
        free_date_cell_key = ".ui-state-default[href]"
        free_date_cell = self.find_element(By.CSS_SELECTOR, free_date_cell_key)

        while not free_date_cell:
            self.select_element(".ui-datepicker-next")
            free_date_cell = self.find_element(By.CSS_SELECTOR, free_date_cell_key)

        quick_sleep()
        free_date_cell.click()

        # Pick latest time
        time_select = Select(
            self.select_element("appointments_consulate_appointment_time")
        )
        option = time_select.options[-1]
        time_select.select_by_value(option.get_attribute("value"))

        if is_prod():
            self.select_element("appointments_consulate_appointment_submit")

    def reschedule_sooner(self):
        """Run all the actions necessary to login and reschedule the appointment
        to a date that is sooner than the currently scheduled appointment.
        """
        logger.debug("> reschedule_sooner")
        self.navigate_login_page()
        self.execute_login()
        self.get_current_appointment()
        self.navigate_reschedule_page()
        self.get_best_date()
        if self.new_appointment:
            self.execute_reschedule()
