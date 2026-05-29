"""Unit tests for constants module."""
import unittest

from autovisa.src.constants import CITY_NAME_ID_MAP, CITY_SLUG_ID_MAP
from autovisa.src.utils import slugify


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

    def test_city_slug_id_map_matches_name_map(self):
        """The pre-computed slug map must stay in sync with the name map.

        Guards against drift now that slugs are hardcoded rather than derived
        at runtime.
        """
        expected = {slugify(name): city_id for name, city_id in CITY_NAME_ID_MAP.items()}
        self.assertEqual(CITY_SLUG_ID_MAP, expected)


if __name__ == '__main__':
    unittest.main()