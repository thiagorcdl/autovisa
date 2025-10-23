import datetime
import re
from functools import cached_property

from selenium.webdriver.common.by import By

from autovisa.src.utils import filter_out_empty, get_month_int


class Appointment:
    """Class to represent an appointment information."""
    date = None
    time = None
    city = None
    applicant_name = None
    passport = None
    ds_160 = None
    element = None

    NO_DATE_REPR = "<No date>"
    ADDRESS_RE_PATTERN = r"\s*(\d+)\s*([a-zA-Z]+)\s*,?\s*(\d+)\s*,?\s*(\d\d:\d\d)\s*([a-zA-Z]+).*"
    INFO_RE_PATTERN = r"([a-zA-Z'\- ]+)\s+(\w{2}\d{6})"

    def __init__(
        self, day, month, year, time, city, applicant_name="",
        passport="", link=None
    ):
        self.date = datetime.date(year, month, day)
        self.time = time
        self.city = city
        self.applicant_name = applicant_name
        self.passport = passport
        self.link = link

    def __repr__(self):
        repr_str = f"{self.date_repr} {self.time} in {self.city}"
        for info in self.applicant_info_list:
            if info:
                repr_str += f" for {info}"
                break
        return repr_str

    @property
    def date_repr(self):
        """Return formatted date."""
        return self.date.strftime("%Y-%m-%d") if self.date else self.NO_DATE_REPR

    @cached_property
    def applicant_info_list(self) -> list:
        return filter_out_empty([self.applicant_name, self.passport])

    def match_applicant(self, applicant_info: str) -> bool:
        """Return whether applicant matches any info in this appointment."""
        return applicant_info in self.applicant_info_list

    @classmethod
    def get_address_from_element(cls, base_element) -> tuple:
        """Parse address from element in the following format:

            <p>Consular Appointment: 21 November, 2023, 11:15 Toronto
               local time at Toronto</p>
       """
        address_element = base_element.find_element(By.CSS_SELECTOR, ".consular-appt")
        # Parse address and time
        day, month_name, year, time, city = [
            result.strip() for result in re.findall(
                cls.ADDRESS_RE_PATTERN,
                address_element.text
            )[0]
        ]
        month = get_month_int(month_name)
        return int(day), month, int(year), time, city

    @classmethod
    def get_applicant_from_element(cls, base_element) -> tuple:
        """Parse applicant information from table element in the following format:

            <tr>
                <td>Jerry Gerônimo</td>
                <td>XY123456</td>
            </tr>
       """
        row_element = base_element.find_element(By.CSS_SELECTOR, "table > tbody > tr")
        return re.findall(
            cls.INFO_RE_PATTERN,
            row_element.text
        )[0]

    @classmethod
    def create_from_element(cls, base_element):
        """Create an Appointment instance from HTML element."""
        day, month, year, time, city = cls.get_address_from_element(base_element)
        name, passport = cls.get_applicant_from_element(base_element)
        link = base_element.find_element(
            By.CSS_SELECTOR, "a.button.primary.small"
        ).get_attribute("href")
        return cls(
            int(day), month, int(year), time, city, name.upper(), passport.upper(),
            link
        )
