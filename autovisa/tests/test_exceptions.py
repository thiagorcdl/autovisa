"""Unit tests for exceptions module."""
import unittest

from autovisa.src.exceptions import MissingDatesException


class TestExceptions(unittest.TestCase):
    """Test cases for custom exceptions."""

    def test_missing_dates_exception_creation(self):
        """Test MissingDatesException can be created."""
        exception = MissingDatesException("No dates available")

        self.assertIsInstance(exception, Exception)
        self.assertEqual(str(exception), "No dates available")

    def test_missing_dates_exception_without_message(self):
        """Test MissingDatesException without message."""
        exception = MissingDatesException()

        self.assertIsInstance(exception, Exception)

    def test_missing_dates_exception_raise(self):
        """Test MissingDatesException can be raised."""
        with self.assertRaises(MissingDatesException):
            raise MissingDatesException("Test error message")


if __name__ == '__main__':
    unittest.main()
