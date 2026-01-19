"""Unit tests for appointment module."""
import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from autovisa.src.appointment import Appointment


class TestAppointment(unittest.TestCase):
    """Test cases for Appointment class."""

    def test_appointment_initialization(self):
        """Test appointment initialization with all parameters."""
        appointment = Appointment(
            day=15,
            month=6,
            year=2023,
            time="10:30",
            city="Toronto",
            applicant_name="John Doe",
            passport="AB123456",
            link="http://example.com"
        )

        self.assertEqual(appointment.date, date(2023, 6, 15))
        self.assertEqual(appointment.time, "10:30")
        self.assertEqual(appointment.city, "Toronto")
        self.assertEqual(appointment.applicant_name, "John Doe")
        self.assertEqual(appointment.passport, "AB123456")
        self.assertEqual(appointment.link, "http://example.com")

    def test_appointment_repr(self):
        """Test appointment string representation."""
        appointment = Appointment(
            day=15, month=6, year=2023, time="10:30", city="Toronto",
            applicant_name="John Doe", passport="AB123456"
        )
        repr_str = repr(appointment)

        self.assertIn("2023-06-15", repr_str)
        self.assertIn("10:30", repr_str)
        self.assertIn("Toronto", repr_str)
        self.assertIn("JOHN DOE", repr_str)

    def test_date_repr(self):
        """Test date representation property."""
        appointment = Appointment(
            day=15, month=6, year=2023, time="10:30", city="Toronto"
        )
        self.assertEqual(appointment.date_repr, "2023-06-15")

    def test_date_repr_none(self):
        """Test date representation when date is None."""
        appointment = Appointment.__new__(Appointment)
        appointment.date = None
        self.assertEqual(appointment.date_repr, Appointment.NO_DATE_REPR)

    def test_applicant_info_list(self):
        """Test applicant info list property."""
        appointment = Appointment(
            day=15, month=6, year=2023, time="10:30", city="Toronto",
            applicant_name="John Doe", passport="AB123456"
        )
        info_list = appointment.applicant_info_list

        self.assertIn("John Doe", info_list)
        self.assertIn("AB123456", info_list)

    def test_match_applicant_by_name(self):
        """Test matching applicant by name."""
        appointment = Appointment(
            day=15, month=6, year=2023, time="10:30", city="Toronto",
            applicant_name="John Doe", passport="AB123456"
        )
        self.assertTrue(appointment.match_applicant("John Doe"))
        self.assertFalse(appointment.match_applicant("Jane Smith"))

    def test_match_applicant_by_passport(self):
        """Test matching applicant by passport."""
        appointment = Appointment(
            day=15, month=6, year=2023, time="10:30", city="Toronto",
            applicant_name="John Doe", passport="AB123456"
        )
        self.assertTrue(appointment.match_applicant("AB123456"))
        self.assertFalse(appointment.match_applicant("CD789012"))


class TestAppointmentClassMethods(unittest.TestCase):
    """Test cases for Appointment class methods."""

    def test_get_address_from_element(self):
        """Test parsing address from HTML element."""
        mock_base_element = MagicMock()
        mock_address_element = MagicMock()
        mock_address_element.text = "Consular Appointment: 21 November, 2023, 11:15 Toronto local time at Toronto"
        mock_base_element.find_element.return_value = mock_address_element

        day, month, year, time, city = Appointment.get_address_from_element(mock_base_element)

        self.assertEqual(day, 21)
        self.assertEqual(month, 11)
        self.assertEqual(year, 2023)
        self.assertEqual(time, "11:15")
        self.assertEqual(city, "Toronto")

    def test_get_applicant_from_element(self):
        """Test parsing applicant information from HTML element."""
        mock_base_element = MagicMock()
        mock_row_element = MagicMock()
        mock_row_element.text = "John Doe XY123456"
        mock_base_element.find_element.return_value = mock_row_element

        name, passport = Appointment.get_applicant_from_element(mock_base_element)

        self.assertEqual(name, "John Doe")
        self.assertEqual(passport, "XY123456")

    @patch('autovisa.src.appointment.Appointment.get_address_from_element')
    @patch('autovisa.src.appointment.Appointment.get_applicant_from_element')
    def test_create_from_element(self, mock_get_applicant, mock_get_address):
        """Test creating Appointment instance from HTML element."""
        mock_base_element = MagicMock()
        mock_get_address.return_value = (21, 11, 2023, "11:15", "Toronto")
        mock_get_applicant.return_value = ("John Doe", "XY123456")

        mock_link_element = MagicMock()
        mock_link_element.get_attribute.return_value = "http://example.com"
        mock_base_element.find_element.return_value = mock_link_element

        appointment = Appointment.create_from_element(mock_base_element)

        self.assertEqual(appointment.date, date(2023, 11, 21))
        self.assertEqual(appointment.time, "11:15")
        self.assertEqual(appointment.city, "Toronto")
        self.assertEqual(appointment.applicant_name, "JOHN DOE")
        self.assertEqual(appointment.passport, "XY123456")
        self.assertEqual(appointment.link, "http://example.com")


if __name__ == '__main__':
    unittest.main()
