"""Shared test helpers for the autovisa unit tests."""
import unittest
from unittest.mock import patch


class OfflineBrowserTestCase(unittest.TestCase):
    """Base test case that stubs out the real browser launch.

    ``WebDriver.__init__`` (inherited by ``Scheduler``) instantiates
    ``DEFAULT_WEBDRIVER_CLASS`` and resolves a local Chrome install; patching
    both keeps construction from spawning an actual Chrome process (and hitting
    the network) per test. ``mock_webdriver_class`` exposes the patched driver
    class for tests that need to assert against the created driver instance.
    """

    def setUp(self):
        super().setUp()
        patchers = [
            patch('autovisa.src.webdriver.DEFAULT_WEBDRIVER_CLASS'),
            patch('autovisa.src.webdriver.get_user_agent',
                  return_value="Test User Agent"),
            patch('autovisa.src.webdriver.get_local_chrome',
                  return_value=("/fake/chrome", "/fake/chromedriver", 140)),
        ]
        self.mock_webdriver_class = patchers[0].start()
        for patcher in patchers[1:]:
            patcher.start()
        for patcher in patchers:
            self.addCleanup(patcher.stop)
