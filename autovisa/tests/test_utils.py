"""Unit tests for utils module."""
import unittest
from unittest.mock import MagicMock, patch

from autovisa.src.utils import (
    is_truthy, is_env, is_prod, is_testing, get_credentials,
    get_user_agent, get_month_int, filter_out_empty, get_response_body,
    get_dict_response
)


class TestIsTruthy(unittest.TestCase):
    """Test cases for is_truthy function."""

    def test_truthy_values(self):
        """Test values that should be truthy."""
        truthy_values = ['1', 'true', 'yes', 'anything', 'True', 'Yes', 'YES', 'test']
        for value in truthy_values:
            self.assertTrue(is_truthy(value), f"Value '{value}' should be truthy")

    def test_falsy_values(self):
        """Test values that should be falsy."""
        falsy_values = ['', '0', 'false', 'no', 'False', 'No', 'NO', 'nO']
        for value in falsy_values:
            self.assertFalse(is_truthy(value), f"Value '{value}' should be falsy")


class TestIsEnv(unittest.TestCase):
    """Test cases for is_env function."""

    @patch.dict('os.environ', {'FALSY_VAR': '0'})
    def test_env_var_falsy(self):
        """Test environment variable with falsy value."""
        self.assertFalse(is_env('FALSY_VAR'))

    @patch.dict('os.environ', {'TRUTHY_VAR': '1'})
    def test_env_var_truthy(self):
        """Test environment variable with truthy value."""
        self.assertTrue(is_env('TRUTHY_VAR'))

    @patch.dict('os.environ', {}, clear=True)
    def test_env_var_missing(self):
        """Test missing environment variable."""
        self.assertFalse(is_env('MISSING_VAR'))


class TestIsProd(unittest.TestCase):
    """Test cases for is_prod function."""

    @patch.dict('os.environ', {'PRODUCTION': '0'})
    def test_not_production(self):
        """Test when not in production mode."""
        self.assertFalse(is_prod())

    @patch.dict('os.environ', {'PRODUCTION': '1'})
    def test_is_production(self):
        """Test when in production mode."""
        self.assertTrue(is_prod())


class TestIsTesting(unittest.TestCase):
    """Test cases for is_testing function."""

    @patch.dict('os.environ', {'TEST': '0'})
    def test_not_testing(self):
        """Test when not in testing mode."""
        self.assertFalse(is_testing())

    @patch.dict('os.environ', {'TEST': '1'})
    def test_is_testing(self):
        """Test when in testing mode."""
        self.assertTrue(is_testing())


class TestGetCredentials(unittest.TestCase):
    """Test cases for get_credentials function."""

    @patch('autovisa.src.utils.is_testing', return_value=True)
    def test_get_credentials_in_testing(self, mock_is_testing):
        """Test getting credentials in testing mode."""
        login, password = get_credentials()
        self.assertIsNotNone(login)
        self.assertIsNotNone(password)

    @patch.dict('os.environ', {'VISA_EMAIL': 'test@example.com', 'VISA_PASSWORD': 'password123'})
    @patch('autovisa.src.utils.is_testing', return_value=False)
    def test_get_credentials_from_env(self, mock_is_testing):
        """Test getting credentials from environment variables."""
        login, password = get_credentials()
        self.assertEqual(login, 'test@example.com')
        self.assertEqual(password, 'password123')

    @patch('autovisa.src.utils.is_testing', return_value=False)
    @patch.dict('os.environ', {}, clear=True)
    def test_get_credentials_missing(self, mock_is_testing):
        """Test missing credentials raises ValueError."""
        with self.assertRaises(ValueError):
            get_credentials()


class TestGetUserAgent(unittest.TestCase):
    """Test cases for get_user_agent function."""

    @patch('autovisa.src.utils.is_testing', return_value=False)
    def test_get_user_agent_production(self, mock_is_testing):
        """Test getting user agent in production mode."""
        user_agent = get_user_agent()
        self.assertIsNotNone(user_agent)
        self.assertIsInstance(user_agent, str)
        self.assertGreater(len(user_agent), 0)


class TestGetMonthInt(unittest.TestCase):
    """Test cases for get_month_int function."""

    def test_month_names(self):
        """Test converting month names to integers."""
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        for i, month_name in enumerate(month_names, 1):
            self.assertEqual(get_month_int(month_name), i)
            self.assertEqual(get_month_int(month_name.lower()), i)
            self.assertEqual(get_month_int(month_name.upper()), i)


class TestFilterOutEmpty(unittest.TestCase):
    """Test cases for filter_out_empty function."""

    def test_filter_empty_values(self):
        """Test filtering out empty values from list."""
        test_list = ['item1', '', 'item2', None, 'item3', '']
        result = filter_out_empty(test_list)
        self.assertEqual(result, ['item1', 'item2', 'item3'])


class TestGetResponseBody(unittest.TestCase):
    """Test cases for get_response_body function."""

    def test_get_response_body(self):
        """Test extracting response body from request."""
        mock_request = MagicMock()
        mock_request.response.body = b'{"test": "data"}'
        mock_request.response.headers = {'Content-Encoding': 'identity'}

        with patch('autovisa.src.utils.decode', return_value=b'{"test": "data"}') as mock_decode:
            result = get_response_body(mock_request)
            mock_decode.assert_called_once_with(
                b'{"test": "data"}',
                'identity'
            )
            self.assertEqual(result, b'{"test": "data"}')


class TestGetDictResponse(unittest.TestCase):
    """Test cases for get_dict_response function."""

    @patch('autovisa.src.utils.get_response_body')
    @patch('json.loads')
    def test_get_dict_response(self, mock_json_loads, mock_get_response_body):
        """Test parsing JSON response as dictionary."""
        mock_get_response_body.return_value = b'[{"date": "2023-01-01"}]'
        mock_json_loads.return_value = [{'date': '2023-01-01'}]

        result = get_dict_response(MagicMock())
        self.assertEqual(result, [{'date': '2023-01-01'}])


if __name__ == '__main__':
    unittest.main()
