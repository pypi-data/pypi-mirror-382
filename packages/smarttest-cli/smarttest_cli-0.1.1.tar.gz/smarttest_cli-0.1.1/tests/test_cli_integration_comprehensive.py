"""
Comprehensive CLI Integration Tests
Tests the complete CLI workflow with PAT token authentication and new dual auth endpoints
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import asyncio

# Import CLI components
from cli.main import execute_scenarios
from cli.config import Config, OutputConfig, ProxyConfig, TLSConfig
from cli.api_client import ApiClient, RateLimitError
from cli.models import ScenarioDefinition, AuthConfigReference

# Import backend for integration testing
from main import app
from database.model import Customer, CustomerRole
from service.AuthService import require_auth


class TestCLIIntegrationComprehensive:
    """Comprehensive test suite for CLI integration with new backend endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application"""
        return TestClient(app)

    @pytest.fixture
    def mock_customer(self):
        """Mock authenticated customer"""
        customer = Mock()
        customer.id = "cli_customer_123"
        customer.email = "cli-test@example.com"
        customer.role = CustomerRole.CLIENT
        return customer

    @pytest.fixture
    def override_auth_dependency(self, mock_customer):
        """Override FastAPI auth dependency for testing"""
        # Clear rate limiter state
        from service.RateLimitService import rate_limiter
        rate_limiter._customer_requests.clear()

        app.dependency_overrides[require_auth] = lambda: mock_customer
        try:
            yield
        finally:
            app.dependency_overrides.pop(require_auth, None)

    @pytest.fixture
    def cli_config(self):
        """CLI configuration for testing"""
        with patch.dict(os.environ, {
            'SMARTTEST_TOKEN': 'st_pat_test_token_12345',
            'SMARTTEST_API_URL': 'http://localhost:8000'
        }):
            config = Config.load()
            yield config

    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file"""
        config_content = {
            'api_url': 'http://localhost:8000',
            'concurrency': 3,
            'timeout': 15,
            'output': {
                'format': 'json',
                'show_progress': False
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            import yaml
            yaml.dump(config_content, f)
            temp_path = f.name

        try:
            yield temp_path
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_cli_scenario_discovery_integration(self, client, override_auth_dependency, cli_config):
        """Test CLI scenario discovery with new backend endpoints"""

        # Mock backend data in the correct API format
        scenario_data = {
            "scenario": {
                "id": 1,
                "name": "Test Scenario"
            },
            "request": {
                "method": "GET",
                "resolved_url": "https://api.example.com/test",
                "headers": {"Content-Type": "application/json"},
                "query": {},
                "body": {"test": "data"}
            },
            "auth_configs": {},
            "validations": [
                {
                    "type": "custom",
                    "validation_text": "status == 200",
                    "description": "Check status"
                }
            ]
        }

        with patch('cli.api_client.ApiClient._request') as mock_request:
            mock_request.return_value = scenario_data

            api_client = ApiClient(cli_config)
            scenario_def = await api_client.get_scenario_definition(1)

            assert scenario_def is not None
            assert scenario_def.id == 1
            assert scenario_def.name == "Test Scenario"
            assert len(scenario_def.validations) == 1
            assert scenario_def.request.method == "GET"

            # Verify API was called with correct endpoint
            mock_request.assert_called_with('GET', '/scenario/1/definition')

    @pytest.mark.asyncio
    async def test_cli_endpoint_scenario_fan_out(self, client, override_auth_dependency, cli_config):
        """Test CLI endpoint scenario fan-out functionality"""

        endpoint_scenarios_data = {
            "scenarios": [
                {"id": 1, "name": "Scenario 1"},
                {"id": 2, "name": "Scenario 2"}
            ],
            "total": 2
        }

        scenario_def_data = {
            "scenario": {
                "id": 1,
                "name": "Scenario 1"
            },
            "request": {
                "method": "GET",
                "resolved_url": "https://api.example.com/test",
                "headers": {},
                "query": {},
                "body": None
            },
            "auth_configs": {},
            "validations": [
                {
                    "type": "custom",
                    "validation_text": "status == 200",
                    "description": "Check status"
                }
            ]
        }

        with patch('cli.api_client.ApiClient._request') as mock_request:
            # Mock endpoint scenarios call and scenario definition calls
            mock_request.side_effect = [
                endpoint_scenarios_data,  # First call to get scenarios
                scenario_def_data,        # Second call to get scenario 1 definition
                scenario_def_data         # Third call to get scenario 2 definition
            ]

            api_client = ApiClient(cli_config)
            scenarios = await api_client.get_endpoint_scenarios(1, only_with_validations=True)

            assert len(scenarios) == 2
            assert all(s.id == 1 for s in scenarios)  # Both return same mock data

            # Verify correct API calls were made
            assert mock_request.call_count == 3
            mock_request.assert_any_call('GET', '/endpoints/1/scenarios', params={'only_with_validations': 'true'})

    @pytest.mark.asyncio
    async def test_cli_system_scenario_discovery(self, client, override_auth_dependency, cli_config):
        """Test CLI system-level scenario discovery"""

        system_scenarios_data = {
            "scenarios": [
                {"id": 1, "name": "System Scenario 1"},
                {"id": 2, "name": "System Scenario 2"}
            ],
            "total": 2
        }

        scenario_def_data = {
            "scenario": {
                "id": 1,
                "name": "System Scenario"
            },
            "request": {
                "method": "POST",
                "resolved_url": "https://api.example.com/system",
                "headers": {},
                "query": {},
                "body": None
            },
            "auth_configs": {},
            "validations": [
                {
                    "type": "custom",
                    "validation_text": "status == 201",
                    "description": "Check creation status"
                }
            ]
        }

        with patch('cli.api_client.ApiClient._request') as mock_request:
            mock_request.side_effect = [
                system_scenarios_data,   # System scenarios call
                scenario_def_data,       # Scenario definition call
                scenario_def_data        # Second scenario definition call
            ]

            api_client = ApiClient(cli_config)
            scenarios = await api_client.get_system_scenarios(1, only_with_validations=True)

            assert len(scenarios) == 2
            mock_request.assert_any_call('GET', '/system/1/scenarios', params={'only_with_validations': 'true'})

    @pytest.mark.asyncio
    async def test_cli_auth_config_references(self, cli_config):
        """Test CLI handling of auth config references (zero-credential exposure)"""

        scenario_with_auth_data = {
            "scenario": {
                "id": 1,
                "name": "Authenticated Scenario"
            },
            "request": {
                "method": "GET",
                "resolved_url": "https://api.example.com/protected",
                "headers": {"Authorization": "${auth_config_1}"},
                "query": {},
                "body": None
            },
            "auth_configs": {
                "auth_config_1": {
                    "id": "auth_config_1",
                    "type": "api_key",
                    "token_param_name": "Authorization",
                    "token_format": "Bearer {token}",
                    "token_usage_location": "header",
                    "system_id": 1,
                    "auth_endpoint": "https://auth.example.com/token",
                    "http_method": "POST",
                    "token_extraction_instruction": "Extract token from response.access_token"
                }
            },
            "validations": [
                {
                    "type": "custom",
                    "validation_text": "status == 200",
                    "description": "Check auth success"
                }
            ]
        }

        with patch('cli.api_client.ApiClient._request') as mock_request:
            mock_request.return_value = scenario_with_auth_data

            api_client = ApiClient(cli_config)
            scenario_def = await api_client.get_scenario_definition(1)

            assert scenario_def is not None
            assert scenario_def.request.headers["Authorization"] == "${auth_config_1}"
            assert len(scenario_def.auth_configs) == 1

            auth_config = scenario_def.auth_configs["auth_config_1"]
            assert auth_config.id == "auth_config_1"
            assert auth_config.type == "api_key"

    @pytest.mark.asyncio
    async def test_cli_scenario_execution_with_results_submission(self, cli_config):
        """Test CLI scenario execution and results submission"""

        execution_data = {
            "http_status": 200,
            "headers": {"content-type": "application/json"},
            "payload": {"result": "success"}
        }

        validation_results = {
            "scenario_id": 1,
            "run_id": 12345,
            "validation_results": {"passed": 1, "failed": 0},
            "total_validations": 1,
            "checked_at": "2024-01-01T12:00:00Z"
        }

        with patch('cli.api_client.ApiClient._request') as mock_request:
            mock_request.return_value = validation_results

            api_client = ApiClient(cli_config)
            results = await api_client.submit_scenario_results(
                scenario_id=1,
                execution_data=execution_data,
                record_run=True,
                increment_usage=True
            )

            assert results["scenario_id"] == 1
            assert results["run_id"] == 12345
            assert results["validation_results"]["passed"] == 1

            # Verify API call was made with correct parameters
            mock_request.assert_called_with(
                'POST',
                '/scenario/1/check-validations',
                params={'record_run': 'true', 'increment_usage': 'true'},
                json=execution_data
            )

    @pytest.mark.asyncio
    async def test_cli_rate_limiting_handling(self, cli_config):
        """Test CLI rate limiting handling and retry logic"""

        with patch('cli.api_client.ApiClient._request') as mock_request:
            # First call triggers rate limit, second succeeds
            mock_request.side_effect = [
                RateLimitError("Rate limit exceeded. Retry after 60 seconds"),
                {"scenario_id": 1, "status": "success"}
            ]

            with patch('asyncio.sleep') as mock_sleep:
                api_client = ApiClient(cli_config)
                results = await api_client.submit_scenario_results(
                    scenario_id=1,
                    execution_data={"http_status": 200},
                    record_run=True,
                    increment_usage=True
                )

                # Should have retried after rate limit (with exponential backoff)
                assert mock_sleep.call_count == 1
                sleep_time = mock_sleep.call_args[0][0]
                assert 60 <= sleep_time <= 180  # Base wait time with exponential backoff
                assert results["scenario_id"] == 1

    def test_cli_config_loading_with_file(self, temp_config_file):
        """Test CLI configuration loading from YAML file"""

        with patch.dict(os.environ, {'SMARTTEST_TOKEN': 'st_pat_file_test_token'}):
            config = Config.load(temp_config_file)

            assert config.token == 'st_pat_file_test_token'  # From environment
            assert config.api_url == 'http://localhost:8000'   # From file
            assert config.concurrency == 3                     # From file
            assert config.timeout == 15                        # From file
            assert config.output.format == 'json'              # From file
            assert config.output.show_progress == False        # From file

    def test_cli_config_environment_precedence(self, temp_config_file):
        """Test configuration precedence (currently file overrides environment)"""

        with patch.dict(os.environ, {
            'SMARTTEST_TOKEN': 'st_pat_env_token',
            'SMARTTEST_API_URL': 'https://env-api.example.com',
            'SMARTTEST_CONCURRENCY': '10'
        }, clear=False):
            config = Config.load(temp_config_file)

            # Token comes from environment (always required from env)
            assert config.token == 'st_pat_env_token'
            # Currently, file config overrides environment variables (current CLI behavior)
            assert config.api_url == 'http://localhost:8000'  # From temp file
            assert config.concurrency == 3  # From temp file

    def test_cli_config_proxy_and_tls_settings(self):
        """Test CLI configuration with proxy and TLS settings"""

        config_content = {
            'proxy': {
                'http_proxy': 'http://proxy.example.com:8080',
                'https_proxy': 'https://proxy.example.com:8080',
                'no_proxy': 'localhost,127.0.0.1'
            },
            'tls': {
                'ca_bundle_path': '/etc/ssl/certs/ca-bundle.crt',
                'verify_ssl': True
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            import yaml
            yaml.dump(config_content, f)
            temp_path = f.name

        try:
            with patch.dict(os.environ, {'SMARTTEST_TOKEN': 'st_pat_proxy_test'}):
                config = Config.load(temp_path)

                assert config.proxy is not None
                assert config.proxy.http_proxy == 'http://proxy.example.com:8080'
                assert config.proxy.https_proxy == 'https://proxy.example.com:8080'
                assert config.proxy.no_proxy == 'localhost,127.0.0.1'

                assert config.tls is not None
                assert config.tls.ca_bundle_path == '/etc/ssl/certs/ca-bundle.crt'
                assert config.tls.verify_ssl == True

                # Test request kwargs include proxy settings
                kwargs = config.get_request_kwargs()
                assert 'proxies' in kwargs
                assert kwargs['proxies']['http'] == 'http://proxy.example.com:8080'
                assert kwargs['verify'] == '/etc/ssl/certs/ca-bundle.crt'

        finally:
            Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_cli_error_handling_and_graceful_degradation(self, cli_config):
        """Test CLI error handling and graceful degradation"""

        with patch('cli.api_client.ApiClient._request') as mock_request:
            # Simulate network error
            mock_request.side_effect = Exception("Network unreachable")

            api_client = ApiClient(cli_config)

            # Should return None for scenario definition errors
            scenario_def = await api_client.get_scenario_definition(1)
            assert scenario_def is None

            # Should return empty list for endpoint scenarios errors
            scenarios = await api_client.get_endpoint_scenarios(1)
            assert scenarios == []

            # Should return fallback result for submission errors
            results = await api_client.submit_scenario_results(1, {"http_status": 200})
            assert results["execution_status"] == "submission_error"
            assert results["summary"]["submission_error"] == True

    @pytest.mark.asyncio
    async def test_cli_full_execution_workflow(self, cli_config):
        """Test complete CLI execution workflow end-to-end"""

        # Mock scenario discovery
        scenario_data = {
            "scenario": {
                "id": 1,
                "name": "E2E Test Scenario"
            },
            "request": {
                "method": "GET",
                "resolved_url": "https://api.example.com/test",
                "headers": {},
                "query": {},
                "body": {}
            },
            "auth_configs": {},
            "validations": [
                {
                    "type": "custom",
                    "validation_text": "status == 200",
                    "description": "Status check"
                }
            ]
        }

        # Mock validation results
        validation_results = {
            "scenario_id": 1,
            "run_id": 999,
            "validation_results": {"passed": 1, "failed": 0},
            "total_validations": 1,
            "execution_status": "success"
        }

        with patch('cli.api_client.ApiClient._request') as mock_request:
            mock_request.side_effect = [scenario_data, validation_results]

            # Mock the scenario executor to avoid actual HTTP requests
            with patch('cli.scenario_executor.ScenarioExecutor.execute_scenarios') as mock_executor:
                from cli.models import ScenarioResult, ExecutionStatus
                mock_result = ScenarioResult(
                    scenario_id=1,
                    scenario_name="E2E Test Scenario",
                    execution_status=ExecutionStatus.SUCCESS,
                    http_status=200,
                    response_time_ms=100
                )
                mock_executor.return_value = [mock_result]

                # Execute full workflow
                exit_code = await execute_scenarios(
                    config=cli_config,
                    scenario_id=1
                )

                # Should complete successfully
                assert exit_code == 0

                # Verify scenario discovery was called
                mock_request.assert_called_with('GET', '/scenario/1/definition')

    def test_cli_authentication_error_messages(self):
        """Test CLI authentication error handling and messages"""

        # Test missing token
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.load()
            assert "SMARTTEST_TOKEN environment variable is required" in str(exc_info.value)

        # Test empty token
        with patch.dict(os.environ, {'SMARTTEST_TOKEN': ''}):
            with pytest.raises(ValueError):
                Config.load()

    @pytest.mark.asyncio
    async def test_cli_concurrent_execution_simulation(self, cli_config):
        """Test CLI concurrent execution capabilities"""

        # Test that configuration supports concurrency settings
        assert cli_config.concurrency == 5  # Default value

        # Test creating multiple API clients (simulating concurrent execution)
        clients = []
        for i in range(cli_config.concurrency):
            client = ApiClient(cli_config)
            clients.append(client)

        # All clients should have the same configuration
        for client in clients:
            assert client.config.token == cli_config.token
            assert client.base_url == cli_config.api_url.rstrip('/')

        # Clean up
        for client in clients:
            await client.close()

    def test_cli_pat_token_security_practices(self, cli_config):
        """Test CLI follows PAT token security best practices"""

        api_client = ApiClient(cli_config)

        # Token should be sent as Bearer token
        auth_header = api_client.client.headers.get('Authorization')
        assert auth_header.startswith('Bearer ')
        assert auth_header == f'Bearer {cli_config.token}'

        # Should have proper User-Agent
        user_agent = api_client.client.headers.get('User-Agent')
        assert 'SmartTest-CLI' in user_agent
        assert '1.0.0' in user_agent

        # Should have timeout configured
        request_kwargs = cli_config.get_request_kwargs()
        assert 'timeout' in request_kwargs
        assert request_kwargs['timeout'] == cli_config.timeout

    def test_cli_invalid_yaml_config_handling(self):
        """Test CLI handling of invalid YAML configuration files"""

        invalid_yaml_content = """
        api_url: https://api.example.com
        concurrency: [invalid yaml structure
        timeout: "not_a_number"
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(invalid_yaml_content)
            temp_path = f.name

        try:
            with patch.dict(os.environ, {'SMARTTEST_TOKEN': 'st_pat_test'}):
                with pytest.raises(ValueError) as exc_info:
                    Config.load(temp_path)
                assert "Invalid YAML" in str(exc_info.value)
        finally:
            Path(temp_path).unlink(missing_ok=True)