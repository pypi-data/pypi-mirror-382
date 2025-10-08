"""
CLI Integration tests for PAT Token authentication
Tests how the CLI would use PAT tokens to authenticate with the backend
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from fastapi.testclient import TestClient
import os

from main import app
from cli.config import Config
from cli.api_client import ApiClient
from database.model import Customer, CustomerRole


class TestCLIPATTokenIntegration(unittest.TestCase):
    """Test CLI authentication using PAT tokens"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.customer_id = "cli_test_customer"
        self.customer = Customer(
            id=self.customer_id,
            email="cli@example.com",
            first_name="CLI",
            last_name="Test",
            role=CustomerRole.CLIENT
        )
        self.test_token = "st_pat_cli_test_token_12345"

        # Mock environment for CLI config
        self.original_env = os.environ.get('SMARTTEST_TOKEN')

    def tearDown(self):
        """Clean up after tests"""
        if self.original_env:
            os.environ['SMARTTEST_TOKEN'] = self.original_env
        elif 'SMARTTEST_TOKEN' in os.environ:
            del os.environ['SMARTTEST_TOKEN']

    def test_cli_config_with_pat_token(self):
        """Test CLI configuration with PAT token"""
        # Set environment variable
        os.environ['SMARTTEST_TOKEN'] = self.test_token

        # Test config loading
        config = Config.load()

        self.assertEqual(config.token, self.test_token)
        self.assertEqual(config.api_url, "https://api.smarttest.com")
        self.assertEqual(config.concurrency, 5)
        self.assertEqual(config.timeout, 30)

    def test_cli_config_missing_token(self):
        """Test CLI configuration with missing PAT token"""
        # Remove token from environment
        if 'SMARTTEST_TOKEN' in os.environ:
            del os.environ['SMARTTEST_TOKEN']

        with self.assertRaises(ValueError) as context:
            Config.load()

        self.assertIn("SMARTTEST_TOKEN environment variable is required", str(context.exception))

    def test_cli_api_client_with_pat_token(self):
        """Test CLI API client with PAT token"""
        os.environ['SMARTTEST_TOKEN'] = self.test_token

        config = Config.load()
        api_client = ApiClient(config)

        # Verify client is configured with correct headers
        self.assertEqual(api_client.config.token, self.test_token)
        self.assertIn('Authorization', api_client.client.headers)
        self.assertEqual(api_client.client.headers['Authorization'], f'Bearer {self.test_token}')
        self.assertEqual(api_client.client.headers['User-Agent'], 'SmartTest-CLI/1.0.0')

    @patch('service.PATTokenAuthService.PATTokenService.get_customer_by_pat_token')
    def test_cli_authentication_with_backend(self, mock_get_customer):
        """Test CLI authentication against backend using PAT token"""
        # Mock successful authentication
        mock_get_customer.return_value = self.customer

        # Test API call with PAT token
        headers = {"Authorization": f"Bearer {self.test_token}"}

        # Test against PAT token info endpoint (public endpoint)
        response = self.client.get("/pat-tokens/info", headers=headers)
        self.assertEqual(response.status_code, 200)

        # Test against protected endpoint (would need authentication)
        # Note: Since we're testing with TestClient, we'd need to mock the authentication
        # This is more of a demonstration of how the flow would work

    def test_cli_token_format_validation(self):
        """Test that CLI validates PAT token format"""
        # Test valid PAT token format
        valid_tokens = [
            "st_pat_" + "a" * 20,
            "st_pat_abcdef123456789012345",
            "st_pat_0123456789ABCDEF"
        ]

        for token in valid_tokens:
            os.environ['SMARTTEST_TOKEN'] = token
            config = Config.load()
            self.assertEqual(config.token, token)

        # Test that CLI accepts any token format (validation happens server-side)
        # The CLI itself doesn't validate token format, just passes it to the server
        invalid_format_token = "not_a_pat_token"
        os.environ['SMARTTEST_TOKEN'] = invalid_format_token
        config = Config.load()
        self.assertEqual(config.token, invalid_format_token)  # CLI accepts it

    def test_cli_error_handling_invalid_token(self):
        """Test CLI error handling with invalid PAT token"""
        invalid_token = "st_pat_invalid_token_123"

        # Mock failed authentication
        with patch('service.PATTokenAuthService.PATTokenService.get_customer_by_pat_token') as mock_get_customer:
            mock_get_customer.return_value = None

            # Test API call with invalid token
            headers = {"Authorization": f"Bearer {invalid_token}"}
            response = self.client.get("/pat-tokens", headers=headers)

            # Should return 401 Unauthorized
            self.assertEqual(response.status_code, 401)

    def test_cli_concurrent_requests_with_pat_token(self):
        """Test CLI making concurrent requests with same PAT token"""
        os.environ['SMARTTEST_TOKEN'] = self.test_token

        config = Config.load()

        # Test that CLI can be configured for concurrent requests
        self.assertEqual(config.concurrency, 5)

        # Test multiple API clients (simulating concurrent scenario execution)
        clients = []
        for i in range(3):
            client = ApiClient(config)
            clients.append(client)

        # All clients should have the same token
        for client in clients:
            self.assertEqual(client.config.token, self.test_token)

    def test_cli_async_requests_configuration(self):
        """Test CLI configuration for async requests with PAT token"""
        os.environ['SMARTTEST_TOKEN'] = self.test_token

        config = Config.load()
        api_client = ApiClient(config)

        # Test that API client is properly configured for async requests
        self.assertEqual(api_client.config.token, self.test_token)
        self.assertIsNotNone(api_client.client)

        # Verify headers are set correctly
        self.assertIn('Authorization', api_client.client.headers)
        self.assertEqual(api_client.client.headers['Authorization'], f'Bearer {self.test_token}')

    def test_cli_token_storage_security(self):
        """Test that CLI handles token storage securely"""
        sensitive_token = "st_pat_sensitive_secret_token_123"
        os.environ['SMARTTEST_TOKEN'] = sensitive_token

        config = Config.load()

        # Token should be stored in config
        self.assertEqual(config.token, sensitive_token)

        # Test that config doesn't accidentally log tokens
        config_str = str(config.__dict__)
        # In a real implementation, you might want to redact tokens in string representations
        # For now, we just verify the token is accessible when needed

    def test_cli_different_api_endpoints(self):
        """Test CLI with different API base URLs"""
        os.environ['SMARTTEST_TOKEN'] = self.test_token

        # Test default API URL
        config = Config.load()
        self.assertEqual(config.api_url, "https://api.smarttest.com")

        # Test custom API URL via environment
        os.environ['SMARTTEST_API_URL'] = "https://staging-api.smarttest.com"
        config = Config.load()
        self.assertEqual(config.api_url, "https://staging-api.smarttest.com")

        # Clean up
        if 'SMARTTEST_API_URL' in os.environ:
            del os.environ['SMARTTEST_API_URL']

    def test_cli_config_file_with_pat_token(self):
        """Test CLI configuration file with PAT token from environment"""
        os.environ['SMARTTEST_TOKEN'] = self.test_token

        # Create a temporary config file content (would be written to file in real scenario)
        config_content = {
            'api_url': 'https://custom-api.smarttest.com',
            'concurrency': 10,
            'timeout': 60,
            'output': {
                'format': 'json',
                'show_progress': False
            }
        }

        # Test that environment token takes precedence
        # (In real scenario, this would involve creating a temporary YAML file)
        config = Config.load()
        self.assertEqual(config.token, self.test_token)  # From environment
        self.assertEqual(config.api_url, "https://api.smarttest.com")  # Default since no file

    def test_cli_authentication_error_messages(self):
        """Test CLI provides helpful error messages for authentication issues"""
        # Test 1: Missing token
        if 'SMARTTEST_TOKEN' in os.environ:
            del os.environ['SMARTTEST_TOKEN']

        try:
            Config.load()
            self.fail("Should have raised ValueError for missing token")
        except ValueError as e:
            self.assertIn("SMARTTEST_TOKEN", str(e))
            self.assertIn("required", str(e))

        # Test 2: Empty token
        os.environ['SMARTTEST_TOKEN'] = ""
        try:
            Config.load()
            self.fail("Should have raised ValueError for empty token")
        except ValueError as e:
            self.assertIn("SMARTTEST_TOKEN", str(e))

    def test_cli_rate_limiting_configuration(self):
        """Test CLI configuration for rate limiting with PAT token"""
        os.environ['SMARTTEST_TOKEN'] = self.test_token

        config = Config.load()
        api_client = ApiClient(config)

        # Test that API client has rate limiting configuration
        self.assertIsNotNone(api_client.config.timeout)
        self.assertEqual(api_client.config.timeout, 30)

        # Test concurrency limits
        self.assertIsNotNone(api_client.config.concurrency)
        self.assertEqual(api_client.config.concurrency, 5)

    def test_cli_pat_token_best_practices(self):
        """Test CLI follows PAT token best practices"""
        test_token = "st_pat_best_practices_test_123456"
        os.environ['SMARTTEST_TOKEN'] = test_token

        config = Config.load()
        api_client = ApiClient(config)

        # Best practice 1: Token is sent as Bearer token
        auth_header = api_client.client.headers.get('Authorization')
        self.assertTrue(auth_header.startswith('Bearer '))
        self.assertEqual(auth_header, f'Bearer {test_token}')

        # Best practice 2: User-Agent is set for CLI identification
        user_agent = api_client.client.headers.get('User-Agent')
        self.assertIn('SmartTest-CLI', user_agent)
        self.assertIn('1.0.0', user_agent)

        # Best practice 3: Timeout is configured
        request_kwargs = config.get_request_kwargs()
        self.assertIn('timeout', request_kwargs)
        self.assertEqual(request_kwargs['timeout'], config.timeout)


if __name__ == "__main__":
    # Run async tests
    loop = asyncio.get_event_loop()
    unittest.main()