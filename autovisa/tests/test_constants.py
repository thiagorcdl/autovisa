"""Unit tests for constants module."""
import unittest

from autovisa.src.constants import CITY_NAME_ID_MAP


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


if __name__ == '__main__':
    unittest.main()