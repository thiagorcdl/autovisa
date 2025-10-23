"""Provide class for scheduling visa."""
import datetime
import logging
import typing as t
from urllib.parse import urlparse

from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.request import Request

from autovisa.src.appointment import Appointment
from autovisa.src.constants import (
    ALLOWED_CITY_IDS, CITY_NAME_ID_MAP, EXCLUDE_DATE_END, EXCLUDE_DATE_START,
    LOGIN_URL, LOGGER_NAME
)
from autovisa.src.utils import (
    get_credentials, get_dict_response,
    is_prod, long_sleep, quick_sleep, rand_sleep, wait_page_load, wait_request
)
from autovisa.src.webdriver import WebDriver

logger = logging.getLogger(LOGGER_NAME)


class Scheduler(WebDriver):
    """Class for encapsulating business logic for scheduling interviews."""
    current_appointment_list: t.Optional[t.List[Appointment]] = None
    current_appointment: t.Optional[Appointment] = None
    new_appointment: t.Optional[Appointment] = None

    def navigate_login_page(self):
        logger.debug("> navigate_login_page")
        self.driver.get(LOGIN_URL)
        wait_page_load()

    def execute_login(self):
        logger.debug("> execute_login")
        """Fill in credentials, consent to privacy policity and try logging in."""
        email, password = get_credentials()

        email_input = self.quick_select_element("user_email")
        self.write_input(email_input, email)

        password_input = self.slow_select_element("user_password")
        self.write_input(password_input, password)

        # Consent to privacy policy
        self.slow_select_element(".icheckbox")

        # Click CTA
        self.slow_select_element("commit")
        wait_page_load()

    def gen_current_appointment_list(self, applicant_info=None):
        """Parse raw text in page and store new Appointment instances."""
        logger.debug("> get_current_appointment_list")
        rand_sleep(1, 2)

        # Find appointment element
        appointment_cards = self.driver.find_elements(
            By.CSS_SELECTOR, ".application.attend_appointment"
        )

        current_appointment_list = []
        for base_element in appointment_cards:
            appointment = Appointment.create_from_element(base_element)
            if applicant_info and appointment.match_applicant(applicant_info):
                current_appointment_list.append(appointment)
                logger.info("Current appointment: %s", appointment)
            else:
                logger.info("Ignored appointment: %s", appointment)
        return current_appointment_list

    def navigate_reschedule_page(self):
        """Expand appropriate section and click CTAs to open the rescheduling page."""
        logger.debug("> navigate_reschedule_page")
        # Click "continue" CTA
        self.slow_select_element("//a[contains(text(), 'Continue')]")
        wait_page_load()

        # Expand "reschedule" section
        self.slow_select_element("//a[.//h5/span[contains(@class, 'fa-calendar-minus')]]")
        # Click "reschedule" CTA
        self.slow_select_element("//a[contains(text(), 'Reschedule Appointment')]")
        wait_page_load()

    def find_json_request(self, city) -> t.Optional[Request]:
        """Traverse requests list multiple times to find the JSON response,
        which contains the available dates.
        """
        logger.debug("> find_json_request")
        wait_request()
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: any(
                    ".json" in urlparse(req.url).path
                    and getattr(req, "response", None) is not None
                    for req in d.requests
                )
            )
        except TimeoutException:
            logger.error("JSON request not found for %s", city)

        for request in self.driver.requests:
            if ".json" in request.path or ".json" in request.url:
                return request
        return None

    def validate_candidate(
            self, candidate, candidate_repr, city
    ) -> bool:
        """Ensure candidate for new best date is sooner than the best ones so far."""
        logger.debug(f"> validate_candidate {candidate}")
        if candidate >= self.current_appointment.date:
            logger.info(
                "Best available date for %s ignored: %s "
                "(later than existing appointment)",
                city, candidate_repr
            )
            return False

        if EXCLUDE_DATE_START <= candidate <= EXCLUDE_DATE_END:
            logger.info(
                "Best date for %s ignored: %s (within exclude date range)",
                city, candidate_repr
            )
            return False
        return True

    def choose_best_date_for_city(self, option_text):
        date_select = self.slow_select_element(
            "appointments_consulate_appointment_date")
        if not date_select:
            # No dates for selected city
            logger.info("No dates for %s", option_text)
            return

        request = self.find_json_request(option_text)
        if not request:
            return

        # Get first date
        response = get_dict_response(request)
        candidate_repr = response[0]["date"]

        year, month, day = list(map(int, candidate_repr.split("-")))
        candidate = datetime.date(year, month, day)
        if not self.validate_candidate(
                candidate, candidate_repr, option_text
        ):
            return
        self.new_appointment = Appointment(day, month, year, "", option_text)

        logger.info("//// New best date found: %s", self.new_appointment)
        return self.new_appointment

    def get_best_date(self) -> Appointment:
        """Find the soonest available date among all cities."""
        logger.debug("> get_best_date")
        if "schedule" not in self.driver.current_url:
            # return  # todo revert
            raise Exception("Session ended")
        self.new_appointment = None

        outside_text = self.instant_select_element(".user-info-footer")
        city_select_element = self.slow_select_element(
            "appointments_consulate_appointment_facility_id")
        city_select = Select(city_select_element)
        n_allowed_cities = len(ALLOWED_CITY_IDS)
        if n_allowed_cities > 1:
            for option in city_select.options:
                city_id = option.get_attribute("value")

                if city_id not in ALLOWED_CITY_IDS:
                    continue

                # Set clean slate / in case of "continue", close the calendar
                city_select_element.send_keys(Keys.ESCAPE)
                outside_text.click()
                city_select_element.click()

                del self.driver.requests

                city_select.select_by_value(city_id)
                new_appointment = self.choose_best_date_for_city(option.text)
                if new_appointment:
                    return new_appointment
        elif n_allowed_cities == 1:
            for city, city_id in CITY_NAME_ID_MAP.items():
                if city_id == ALLOWED_CITY_IDS[0]:
                    return self.choose_best_date_for_city(city)

    def execute_reschedule(self):
        """Select the info for the best appointment found."""
        logger.debug("> execute_reschedule")
        city_select = Select(
            self.slow_select_element("appointments_consulate_appointment_facility_id")
        )
        city_select.select_by_value(CITY_NAME_ID_MAP[self.new_appointment.city])

        # Select soonest date in calendar
        self.slow_select_element("appointments_consulate_appointment_date")
        free_date_cell_key = ".ui-state-default[href]"
        free_date_cell = self.find_element(By.CSS_SELECTOR, free_date_cell_key)

        while not free_date_cell:
            self.quick_select_element(".ui-datepicker-next")
            free_date_cell = self.find_element(By.CSS_SELECTOR, free_date_cell_key)

        quick_sleep()
        free_date_cell.click()

        # Pick latest time
        logger.info("///// Picking latest time")
        time_select = Select(
            self.slow_select_element("appointments_consulate_appointment_time")
        )
        option = time_select.options[-1]
        time_select.select_by_value(option.get_attribute("value"))

        self.slow_select_element("appointments_consulate_appointment_submit")
        if is_prod():
            # Confirm modal
            logger.info("///// Confirming")
            self.slow_select_element(
                "body > div.reveal-overlay > div > div > a.button.alert"
            )

    def reschedule_current_appointment(self):
        logger.debug(f"> reschedule_current_appointment {self.current_appointment}")
        self.navigate_reschedule_page()
        self.get_best_date()

        if len(self.current_appointment_list) == 1:
            # Stay in page to retry single match
            while not self.new_appointment:
                logger.info("... No good appointments found.")
                long_sleep()
                self.driver.refresh()
                logger.info("... Checking cities again.")
                self.get_best_date()

        self.execute_reschedule()
        self.current_appointment = None
        self.new_appointment = None

    def run_reschedule_suite(self, applicant_info=None):
        """Run all the actions necessary to log in and reschedule the appointment
        to a date that is sooner than the currently scheduled appointment.
        """
        logger.debug("> run_reschedule_suite")
        self.navigate_login_page()
        self.execute_login()
        self.current_appointment_list = self.gen_current_appointment_list(applicant_info)

        if not self.current_appointment_list:
            logger.error("No upcoming appointments found!")
            return

        appointment_list_url = self.driver.current_url
        for appointment in self.current_appointment_list:
            self.current_appointment = appointment
            self.reschedule_current_appointment()
            self.driver.get(appointment_list_url)
