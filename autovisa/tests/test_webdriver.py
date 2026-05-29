"""Unit tests for webdriver module."""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

from autovisa.src.webdriver import WebDriver


class TestWebDriver(unittest.TestCase):
    """Test cases for WebDriver class."""

    def setUp(self):
        """Stub out the real browser launch so these unit tests run offline.

        ``WebDriver.__init__`` instantiates ``DEFAULT_WEBDRIVER_CLASS`` and
        resolves a local Chrome install; patching both keeps construction from
        spawning an actual Chrome process (and hitting the network) per test.
        """
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

    def test_webdriver_initialization(self):
        """Test WebDriver initialization."""
        mock_driver_instance = MagicMock()
        self.mock_webdriver_class.return_value = mock_driver_instance

        web_driver = WebDriver()

        self.assertIsNotNone(web_driver.driver)
        mock_driver_instance.execute_cdp_cmd.assert_called_once()

    @patch('autovisa.src.webdriver.get_user_agent')
    def test_get_driver_args_chrome(self, mock_get_user_agent):
        """Test get_driver_args for Chrome driver."""
        mock_get_user_agent.return_value = "Test User Agent"

        web_driver = WebDriver()
        web_driver._WEBDRIVER_CLASS = MagicMock()

        with patch('autovisa.src.webdriver.webdriver.Chrome'):
            driver_args, driver_kwargs = web_driver.get_driver_args()

            self.assertIsInstance(driver_args, list)
            self.assertIsInstance(driver_kwargs, dict)

    @patch('autovisa.src.webdriver.webdriver.Chrome')
    def test_get_driver_args_firefox(self, mock_firefox):
        """Test get_driver_args for Firefox driver."""
        web_driver = WebDriver()
        web_driver._WEBDRIVER_CLASS = mock_firefox
        web_driver.driver = MagicMock()

        with patch('autovisa.src.webdriver.webdriver.Firefox'):
            with patch('autovisa.src.webdriver.webdriver.FirefoxProfile') as mock_profile:
                driver_args, driver_kwargs = web_driver.get_driver_args()

                self.assertIsInstance(driver_args, list)
                self.assertIsInstance(driver_kwargs, dict)

    def test_find_element_success(self):
        """Test successful element finding."""
        web_driver = WebDriver()
        web_driver.driver = MagicMock()
        mock_element = MagicMock()
        web_driver.driver.find_element.return_value = mock_element

        result = web_driver.find_element("ID", "test-id")

        self.assertEqual(result, mock_element)

    def test_find_element_not_found(self):
        """Test element not found case."""
        from selenium.common import NoSuchElementException
        from selenium.common import InvalidSelectorException

        web_driver = WebDriver()
        web_driver.driver = MagicMock()
        web_driver.driver.find_element.side_effect = NoSuchElementException()

        result = web_driver.find_element("ID", "test-id")

        self.assertIsNone(result)

    def test_instant_select_element_success(self):
        """Test successful instant element selection and clicking."""
        web_driver = WebDriver()
        web_driver.driver = MagicMock()
        mock_element = MagicMock()
        web_driver.find_element = MagicMock(return_value=mock_element)

        result = web_driver.instant_select_element("test-id")

        self.assertEqual(result, mock_element)
        mock_element.click.assert_called_once()

    def test_instant_select_element_not_interactable(self):
        """Test element not interactable case."""
        from selenium.common import ElementNotInteractableException

        web_driver = WebDriver()
        web_driver.driver = MagicMock()
        mock_element = MagicMock()
        mock_element.click.side_effect = ElementNotInteractableException()
        web_driver.find_element = MagicMock(return_value=mock_element)

        result = web_driver.instant_select_element("test-id")

        self.assertIsNone(result)

    def test_instant_select_element_stale_retry_succeeds(self):
        """Test that a stale element on click is retried and eventually clicked."""
        from selenium.common import StaleElementReferenceException

        web_driver = WebDriver()
        web_driver.driver = MagicMock()
        mock_element = MagicMock()
        # Stale on the first attempt, then a clean click on the retry.
        mock_element.click.side_effect = [StaleElementReferenceException(), None]
        web_driver.find_element = MagicMock(return_value=mock_element)

        result = web_driver.instant_select_element("test-id")

        self.assertEqual(result, mock_element)
        self.assertEqual(mock_element.click.call_count, 2)

    def test_instant_select_element_stale_exhausts_attempts(self):
        """Test that persistent staleness gives up after MAX_CLICK_ATTEMPTS."""
        from selenium.common import StaleElementReferenceException
        from autovisa.src.constants import MAX_CLICK_ATTEMPTS

        web_driver = WebDriver()
        web_driver.driver = MagicMock()
        mock_element = MagicMock()
        mock_element.click.side_effect = StaleElementReferenceException()
        web_driver.find_element = MagicMock(return_value=mock_element)

        result = web_driver.instant_select_element("test-id")

        self.assertIsNone(result)
        self.assertEqual(mock_element.click.call_count, MAX_CLICK_ATTEMPTS)

    def test_instant_select_element_attempt_over_limit(self):
        """Test that an attempt past the limit returns immediately without searching."""
        from autovisa.src.constants import MAX_CLICK_ATTEMPTS

        web_driver = WebDriver()
        web_driver.driver = MagicMock()
        web_driver.find_element = MagicMock()

        result = web_driver.instant_select_element(
            "test-id", attempt=MAX_CLICK_ATTEMPTS + 1
        )

        self.assertIsNone(result)
        web_driver.find_element.assert_not_called()

    @patch('autovisa.src.webdriver.delayed')
    def test_slow_select_element(self, mock_delayed):
        """Test slow_select_element uses delayed decorator."""
        web_driver = WebDriver()
        web_driver.instant_select_element = MagicMock()
        mock_element = MagicMock()
        web_driver.instant_select_element.return_value = mock_element

        result = web_driver.slow_select_element("test-id")

        self.assertEqual(result, mock_element)

    @patch('autovisa.src.webdriver.quick_delayed')
    def test_quick_select_element(self, mock_quick_delayed):
        """Test quick_select_element uses quick_delayed decorator."""
        web_driver = WebDriver()
        web_driver.instant_select_element = MagicMock()
        mock_element = MagicMock()
        web_driver.instant_select_element.return_value = mock_element

        result = web_driver.quick_select_element("test-id")

        self.assertEqual(result, mock_element)

    @patch('autovisa.src.webdriver.random.choice')
    def test_select_random_element(self, mock_choice):
        """Test random element selection."""
        web_driver = WebDriver()
        web_driver.slow_select_element = MagicMock()
        mock_element = MagicMock()
        web_driver.slow_select_element.return_value = mock_element
        mock_choice.return_value = "random-selector"

        selectors = ["selector1", "selector2", "selector3"]

        result = web_driver.select_random_element(selectors)

        self.assertEqual(result, mock_element)
        web_driver.slow_select_element.assert_called_once_with("random-selector")

    @patch('autovisa.src.webdriver.quick_sleep')
    def test_write_input(self, mock_quick_sleep):
        """Test writing text to input element character by character."""
        web_driver = WebDriver()
        web_driver.driver = MagicMock()
        mock_element = MagicMock()

        web_driver.write_input(mock_element, "test")

        self.assertEqual(mock_element.send_keys.call_count, 4)
        calls = [call[0][0] for call in mock_element.send_keys.call_args_list]
        self.assertEqual(calls, ['t', 'e', 's', 't'])


if __name__ == '__main__':
    unittest.main()
