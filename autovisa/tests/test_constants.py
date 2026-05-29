"""Unit tests for constants module."""
import unittest

from autovisa.src.constants import CITY_SLUG_ID_MAP
from autovisa.src.utils import slugify


class TestConstants(unittest.TestCase):
    """Test cases for constants module."""

    def test_city_slug_id_map_structure(self):
        """Test that CITY_SLUG_ID_MAP has the expected structure."""
        self.assertIsInstance(CITY_SLUG_ID_MAP, dict)
        self.assertGreater(len(CITY_SLUG_ID_MAP), 0)

        for slug, city_id in CITY_SLUG_ID_MAP.items():
            self.assertIsInstance(slug, str)
            self.assertIsInstance(city_id, str)
            self.assertTrue(city_id.isdigit())
            # Keys must already be in canonical slug form.
            self.assertEqual(slug, slugify(slug))


if __name__ == '__main__':
    unittest.main()