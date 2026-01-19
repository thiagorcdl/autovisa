"""Unit tests for constants module."""
import unittest
from datetime import date

from autovisa.src.constants import (
    CITY_NAME_ID_MAP, EXCLUDE_DATE_START, EXCLUDE_DATE_END, ALLOWED_CITY_IDS
)


class TestConstants(unittest.TestCase):
    """Test cases for constants module."""

    def test_city_name_id_map_structure(self):
        """Test that CITY_NAME_ID_MAP has the expected structure."""
        self.assertIsInstance(CITY_NAME_ID_MAP, dict)
        self.assertGreater(len(CITY_NAME_ID_MAP), 0)
        
        for city_name, city_id in CITY_NAME_ID_MAP.items():
            self.assertIsInstance(city_name, str)
            self.assertIsInstance(city_id, str)
            self.assertTrue(city_id.isdigit())

    def test_exclude_date_range(self):
        """Test that EXCLUDE_DATE_START and EXCLUDE_DATE_END are valid dates."""
        self.assertIsInstance(EXCLUDE_DATE_START, date)
        self.assertIsInstance(EXCLUDE_DATE_END, date)
        self.assertLess(EXCLUDE_DATE_START, EXCLUDE_DATE_END)

    def test_allowed_city_ids(self):
        """Test that ALLOWED_CITY_IDS is a tuple of strings."""
        self.assertIsInstance(ALLOWED_CITY_IDS, tuple)
        for city_id in ALLOWED_CITY_IDS:
            self.assertIsInstance(city_id, str)
            self.assertTrue(city_id.isdigit())


if __name__ == '__main__':
    unittest.main()