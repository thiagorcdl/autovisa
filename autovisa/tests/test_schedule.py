"""Unit tests for schedule module."""
import unittest
from datetime import date
from unittest.mock import MagicMock, patch, PropertyMock

from autovisa.src.schedule import Scheduler
from autovisa.src.appointment import Appointment


class TestScheduler(unittest.TestCase):
    """Test cases for Scheduler class."""

    @patch('autovisa.src.schedule.WebDriver')
    def test_scheduler_initialization(self, mock_webdriver):
        """Test Scheduler initialization."""
        scheduler = Scheduler()

        self.assertIsNone(scheduler.current_appointment_list)
        self.assertIsNone(scheduler.current_appointment)
        self.assertIsNone(scheduler.new_appointment)

    def test_navigate_login_page(self):
        """Test navigating to login page."""
        scheduler = Scheduler()
        scheduler.driver = MagicMock()

        with patch.dict('os.environ', {'BASE_URL': 'https://example.com'}):
            with patch('autovisa.src.schedule.wait_page_load'):
                scheduler.navigate_login_page()

                scheduler.driver.get.assert_called_once()

    def test_execute_login(self):
        """Test executing login."""
        scheduler = Scheduler()
        scheduler.driver = MagicMock()
        mock_email_input = MagicMock()
        mock_password_input = MagicMock()

        with patch('autovisa.src.schedule.get_credentials', return_value=('test@example.com', 'password')):
            with patch('autovisa.src.schedule.wait_page_load'):
                scheduler.quick_select_element = MagicMock(return_value=mock_email_input)
                scheduler.slow_select_element = MagicMock(return_value=mock_password_input)
                scheduler.write_input = MagicMock()

                scheduler.execute_login()

                scheduler.write_input.assert_any_call(mock_email_input, 'test@example.com')
                scheduler.write_input.assert_any_call(mock_password_input, 'password')

    def test_gen_current_appointment_list(self):
        """Test generating current appointment list."""
        scheduler = Scheduler()
        scheduler.driver = MagicMock()

        mock_base_element = MagicMock()
        scheduler.driver.find_elements.return_value = [mock_base_element]

        with patch('autovisa.src.schedule.rand_sleep'):
            with patch('autovisa.src.schedule.Appointment.create_from_element') as mock_create:
                mock_appointment = MagicMock()
                mock_appointment.match_applicant.return_value = True
                mock_create.return_value = mock_appointment

                result = scheduler.gen_current_appointment_list("APPLICANT")

                self.assertEqual(len(result), 1)

    def test_navigate_reschedule_page(self):
        """Test navigating to reschedule page."""
        scheduler = Scheduler()
        scheduler.driver = MagicMock()

        with patch('autovisa.src.schedule.wait_page_load'):
            scheduler.slow_select_element = MagicMock()
            scheduler.navigate_reschedule_page()

            self.assertEqual(scheduler.slow_select_element.call_count, 3)

    def test_find_json_request(self):
        """Test finding JSON request."""
        scheduler = Scheduler()
        scheduler.driver = MagicMock()

        mock_request = MagicMock()
        mock_request.path = '/test.json'
        scheduler.driver.requests = [mock_request]

        with patch('autovisa.src.schedule.wait_request'):
            with patch('autovisa.src.schedule.WebDriverWait'):
                result = scheduler.find_json_request("Toronto")

                self.assertEqual(result, mock_request)

    def test_validate_candidate(self):
        """Test candidate date validation."""
        scheduler = Scheduler()
        scheduler.current_appointment = Appointment(
            day=20, month=6, year=2023, time="10:30", city="Toronto"
        )

        candidate_date = date(2023, 6, 15)
        candidate_repr = "2023-06-15"
        city = "Toronto"

        result = scheduler.validate_candidate(candidate_date, candidate_repr, city)

        self.assertTrue(result)

    def test_validate_candidate_later_date(self):
        """Test candidate validation for later date."""
        scheduler = Scheduler()
        scheduler.current_appointment = Appointment(
            day=15, month=6, year=2023, time="10:30", city="Toronto"
        )

        candidate_date = date(2023, 6, 20)
        candidate_repr = "2023-06-20"
        city = "Toronto"

        result = scheduler.validate_candidate(candidate_date, candidate_repr, city)

        self.assertFalse(result)

    def test_execute_reschedule(self):
        """Test executing reschedule."""
        scheduler = Scheduler()
        scheduler.driver = MagicMock()
        scheduler.new_appointment = MagicMock()
        scheduler.new_appointment.city = "Toronto"

        mock_city_select = MagicMock()
        mock_time_select = MagicMock()
        mock_option = MagicMock()
        mock_option.get_attribute.return_value = "value"
        mock_time_select.options = [mock_option]

        with patch('autovisa.src.schedule.is_prod', return_value=False):
            with patch('autovisa.src.schedule.Select') as mock_select_class:
                mock_select_class.side_effect = [mock_city_select, mock_time_select]

                with patch('autovisa.src.schedule.quick_sleep'):
                    with patch('autovisa.src.schedule.selenium.webdriver.common.by.By.CSS_SELECTOR'):
                        result = scheduler.execute_reschedule()

                        self.assertTrue(result)

    def test_run_reschedule_suite(self):
        """Test running complete reschedule suite."""
        scheduler = Scheduler()
        scheduler.driver = MagicMock()
        scheduler.current_appointment_list = [MagicMock()]

        with patch('autovisa.src.schedule.wait_page_load'):
            scheduler.navigate_login_page = MagicMock()
            scheduler.execute_login = MagicMock()
            scheduler.gen_current_appointment_list = MagicMock(return_value=[])
            scheduler.reschedule_current_appointment = MagicMock()

            scheduler.run_reschedule_suite()

            scheduler.navigate_login_page.assert_called_once()
            scheduler.execute_login.assert_called_once()
            scheduler.gen_current_appointment_list.assert_called_once()


if __name__ == '__main__':
    unittest.main()
