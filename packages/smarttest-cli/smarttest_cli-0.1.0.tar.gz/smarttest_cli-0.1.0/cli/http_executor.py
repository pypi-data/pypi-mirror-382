"""HTTP execution engine for running test scenarios."""

import time
import asyncio
import json
from typing import Dict, Any, Optional, Tuple
import httpx

from .config import Config
from .models import HttpRequest, ExecutionStatus, ScenarioResult, ValidationResult
from .auth_resolver import AuthResolver, AuthResolutionError

class HttpExecutor:
    """
    HTTP execution engine that handles:
    - Secure auth resolution (zero credential exposure)
    - Request execution with proper error handling
    - Response capture and error classification
    - Network timeout and error handling as per MVP spec
    """

    def __init__(self, config: Config):
        self.config = config
        self.auth_resolver = AuthResolver()

        # Create HTTP client with configuration (exclude timeout - we'll pass per-request)
        client_kwargs = config.get_request_kwargs()
        client_kwargs.pop('timeout', None)  # Remove timeout from client kwargs
        self.client = httpx.AsyncClient(**client_kwargs)

    async def close(self):
        """Clean up resources."""
        await self.client.aclose()
        self.auth_resolver.clear_cache()

    async def execute_scenario(
        self,
        scenario_definition,
        api_client
    ) -> ScenarioResult:
        """
        Execute a single scenario with comprehensive error handling.

        Returns ScenarioResult with proper execution status classification
        as defined in the MVP specification.
        """
        start_time = time.time()
        scenario_id = scenario_definition.id
        scenario_name = scenario_definition.name

        try:
            # Step 1: Resolve authentication (critical security step)
            try:
                resolved_request = self.auth_resolver.resolve_auth_configs(
                    scenario_definition.auth_configs,
                    scenario_definition.request
                )
            except AuthResolutionError as e:
                return self._create_error_result(
                    scenario_id=scenario_id,
                    scenario_name=scenario_name,
                    execution_status=ExecutionStatus.AUTH_ERROR,
                    error_message=str(e),
                    start_time=start_time
                )

            # Step 2: Execute HTTP request
            execution_data, execution_status = await self._execute_http_request(resolved_request)

            # Step 3: Submit results to backend for validation (if successful)
            if execution_status == ExecutionStatus.SUCCESS:
                validation_response = await api_client.submit_scenario_results(
                    scenario_id=scenario_id,
                    execution_data=execution_data,
                    record_run=True,
                    increment_usage=True
                )

                # Parse validation results
                validation_results = self._parse_validation_results(
                    validation_response.get('validations', [])
                )

                result = ScenarioResult(
                    scenario_id=scenario_id,
                    scenario_name=scenario_name,
                    execution_status=execution_status,
                    http_status=execution_data.get('http_status'),
                    response_time_ms=execution_data.get('response_time_ms'),
                    validation_results=validation_results,
                    run_id=validation_response.get('run_id')
                )
                # Propagate endpoint metadata for grouped display
                if hasattr(scenario_definition, '_endpoint_method'):
                    result._endpoint_method = scenario_definition._endpoint_method
                if hasattr(scenario_definition, '_endpoint_path'):
                    result._endpoint_path = scenario_definition._endpoint_path
                return result
            else:
                # For non-successful executions, still submit for record keeping
                try:
                    validation_response = await api_client.submit_scenario_results(
                        scenario_id=scenario_id,
                        execution_data=execution_data,
                        record_run=True,
                        increment_usage=True
                    )
                    run_id = validation_response.get('run_id')
                except:
                    run_id = None

                result = ScenarioResult(
                    scenario_id=scenario_id,
                    scenario_name=scenario_name,
                    execution_status=execution_status,
                    http_status=execution_data.get('http_status'),
                    response_time_ms=execution_data.get('response_time_ms'),
                    error_details=execution_data.get('error_details'),
                    run_id=run_id
                )
                # Propagate endpoint metadata for grouped display
                if hasattr(scenario_definition, '_endpoint_method'):
                    result._endpoint_method = scenario_definition._endpoint_method
                if hasattr(scenario_definition, '_endpoint_path'):
                    result._endpoint_path = scenario_definition._endpoint_path
                return result

        except Exception as e:
            return self._create_error_result(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                execution_status=ExecutionStatus.UNKNOWN_ERROR,
                error_message=str(e),
                start_time=start_time
            )

    async def _execute_http_request(
        self,
        request: HttpRequest
    ) -> Tuple[Dict[str, Any], ExecutionStatus]:
        """
        Execute HTTP request with proper error classification.

        Returns tuple of (execution_data, execution_status) as per MVP spec.
        """
        start_time = time.time()

        try:
            # Prepare request parameters - only include non-empty values
            request_kwargs = {
                'method': request.method,
                'url': request.resolved_url,
                'timeout': httpx.Timeout(self.config.timeout, connect=10.0)
            }
            
            if request.headers:
                request_kwargs['headers'] = request.headers
            
            if request.query:
                request_kwargs['params'] = request.query
            
            # Add body if present (skip empty lists/dicts)
            if request.body is not None and request.body != [] and request.body != {}:
                if isinstance(request.body, dict):
                    request_kwargs['json'] = request.body
                else:
                    request_kwargs['content'] = request.body

            # Execute request
            response = await self.client.request(**request_kwargs)
            response_time_ms = int((time.time() - start_time) * 1000)

            # Prepare execution data for successful requests
            execution_data = {
                'execution_status': 'success',
                'http_status': response.status_code,
                'headers': dict(response.headers),
                'response_time_ms': response_time_ms
            }

            # Try to parse response body
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    execution_data['payload'] = response.json()
                else:
                    execution_data['payload'] = response.text
            except:
                execution_data['payload'] = response.content.decode('utf-8', errors='ignore')

            # Classify execution status based on HTTP status
            if response.status_code >= 400:
                return execution_data, ExecutionStatus.HTTP_ERROR
            else:
                return execution_data, ExecutionStatus.SUCCESS

        except httpx.TimeoutException:
            response_time_ms = int((time.time() - start_time) * 1000)
            execution_data = {
                'execution_status': 'network_timeout',
                'http_status': None,
                'headers': None,
                'payload': None,
                'response_time_ms': response_time_ms,
                'error_details': {
                    'error_type': 'TimeoutException',
                    'message': f'Request timeout after {self.config.timeout}s'
                }
            }
            return execution_data, ExecutionStatus.NETWORK_TIMEOUT

        except (httpx.ConnectError, httpx.NetworkError) as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            execution_data = {
                'execution_status': 'network_error',
                'http_status': None,
                'headers': None,
                'payload': None,
                'response_time_ms': response_time_ms,
                'error_details': {
                    'error_type': type(e).__name__,
                    'message': str(e)
                }
            }
            return execution_data, ExecutionStatus.NETWORK_ERROR

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            execution_data = {
                'execution_status': 'unknown_error',
                'http_status': None,
                'headers': None,
                'payload': None,
                'response_time_ms': response_time_ms,
                'error_details': {
                    'error_type': type(e).__name__,
                    'message': str(e)
                }
            }
            return execution_data, ExecutionStatus.UNKNOWN_ERROR

    def _parse_validation_results(self, validations_data: list) -> list[ValidationResult]:
        """Parse validation results from API response."""
        results = []
        for i, validation in enumerate(validations_data):
            results.append(ValidationResult(
                validation_id=validation.get('id', i),
                name=validation.get('name', f'validation_{i}'),
                passed=validation.get('passed', False),
                details=validation.get('details')
            ))
        return results

    def _create_error_result(
        self,
        scenario_id: int,
        scenario_name: str,
        execution_status: ExecutionStatus,
        error_message: str,
        start_time: float
    ) -> ScenarioResult:
        """Create error result for failed scenario execution."""
        response_time_ms = int((time.time() - start_time) * 1000)

        return ScenarioResult(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            execution_status=execution_status,
            response_time_ms=response_time_ms,
            error_details={
                'error_type': execution_status.value,
                'message': error_message
            }
        )