"""API client for communicating with SmartTest backend."""

import httpx
from typing import List, Dict, Any, Optional
import asyncio
import traceback
import sys
from dataclasses import dataclass

from .config import Config
from .models import ScenarioDefinition, AuthConfigReference

class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after

class ApiClient:
    """HTTP client for SmartTest backend API with rate limiting awareness."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.api_url.rstrip('/')

        # Create HTTP client with configuration
        client_kwargs = config.get_request_kwargs()
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                'Authorization': f'Bearer {config.token}',
                'User-Agent': 'SmartTest-CLI/1.0.0'
            },
            **client_kwargs
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling and rate limiting awareness."""
        full_url = f"{self.base_url}{path}"

        try:
            response = await self.client.request(method, path, **kwargs)

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"\n⚠️  [RATE LIMIT]", file=sys.stderr)
                print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
                print(f"   Status: 429 Too Many Requests", file=sys.stderr)
                print(f"   Retry after: {retry_after} seconds", file=sys.stderr)
                print(f"   Note: SmartTest API limits scenario endpoints to 20 requests/minute", file=sys.stderr)
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds",
                    retry_after=retry_after
                )

            # Handle other HTTP errors
            response.raise_for_status()

            return response.json()

        except httpx.TimeoutException as e:
            print(f"\n❌ [TIMEOUT ERROR]", file=sys.stderr)
            print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
            print(f"   Error: Request timed out after {self.config.timeout}s", file=sys.stderr)
            print(f"   Suggestion: Increase timeout with SMARTTEST_TIMEOUT or check if API is responsive", file=sys.stderr)
            print(f"   Details: {type(e).__name__}: {str(e)}", file=sys.stderr)
            raise Exception(f"Request timeout after {self.config.timeout}s: {full_url}")

        except httpx.ConnectError as e:
            print(f"\n❌ [CONNECTION ERROR]", file=sys.stderr)
            print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
            print(f"   Error: Could not connect to SmartTest API", file=sys.stderr)
            print(f"   Configured API URL: {self.base_url}", file=sys.stderr)
            print(f"   Suggestion: Check if the API server is running and SMARTTEST_API_URL is correct", file=sys.stderr)
            print(f"   Details: {type(e).__name__}: {str(e)}", file=sys.stderr)
            raise Exception(f"Connection failed to {full_url}: {str(e)}")

        except httpx.NetworkError as e:
            print(f"\n❌ [NETWORK ERROR]", file=sys.stderr)
            print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
            print(f"   Error: Network issue occurred", file=sys.stderr)
            print(f"   Details: {type(e).__name__}: {str(e)}", file=sys.stderr)
            print(f"   Suggestion: Check your network connection and firewall settings", file=sys.stderr)
            raise Exception(f"Network error: {str(e)}")

        except httpx.RequestError as e:
            print(f"\n❌ [REQUEST ERROR]", file=sys.stderr)
            print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
            print(f"   Error: Failed to send request", file=sys.stderr)
            print(f"   Details: {type(e).__name__}: {str(e)}", file=sys.stderr)
            if hasattr(e, '__cause__') and e.__cause__:
                print(f"   Root cause: {type(e.__cause__).__name__}: {str(e.__cause__)}", file=sys.stderr)
            raise Exception(f"Request error: {str(e)}")

        except httpx.HTTPStatusError as e:
            response_text = e.response.text[:500]  # Limit to 500 chars

            if e.response.status_code == 401:
                print(f"\n❌ [AUTHENTICATION ERROR]", file=sys.stderr)
                print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
                print(f"   Status: 401 Unauthorized", file=sys.stderr)
                print(f"   Error: Authentication failed", file=sys.stderr)
                print(f"   Suggestion: Check your SMARTTEST_TOKEN environment variable", file=sys.stderr)
                print(f"   Response: {response_text}", file=sys.stderr)
                raise Exception("Authentication failed. Please check your SMARTTEST_TOKEN")

            elif e.response.status_code == 403:
                print(f"\n❌ [AUTHORIZATION ERROR]", file=sys.stderr)
                print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
                print(f"   Status: 403 Forbidden", file=sys.stderr)
                print(f"   Error: Access forbidden", file=sys.stderr)
                print(f"   Suggestion: Your token doesn't have permission to access this resource", file=sys.stderr)
                print(f"   Response: {response_text}", file=sys.stderr)
                raise Exception("Access forbidden. Please check your permissions")

            elif e.response.status_code == 404:
                print(f"\n❌ [NOT FOUND ERROR]", file=sys.stderr)
                print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
                print(f"   Status: 404 Not Found", file=sys.stderr)
                print(f"   Error: Resource not found", file=sys.stderr)
                print(f"   Suggestion: Check if the scenario/endpoint/system ID exists", file=sys.stderr)
                print(f"   Response: {response_text}", file=sys.stderr)
                raise Exception(f"Resource not found: {path}")

            elif e.response.status_code >= 500:
                print(f"\n❌ [SERVER ERROR]", file=sys.stderr)
                print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
                print(f"   Status: {e.response.status_code}", file=sys.stderr)
                print(f"   Error: SmartTest API server error", file=sys.stderr)
                print(f"   Suggestion: The API server encountered an error. Try again or contact support", file=sys.stderr)
                print(f"   Response: {response_text}", file=sys.stderr)
                raise Exception(f"API server error ({e.response.status_code}): {response_text}")

            else:
                print(f"\n❌ [HTTP ERROR]", file=sys.stderr)
                print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
                print(f"   Status: {e.response.status_code}", file=sys.stderr)
                print(f"   Error: HTTP error occurred", file=sys.stderr)
                print(f"   Response: {response_text}", file=sys.stderr)
                raise Exception(f"API error ({e.response.status_code}): {response_text}")

        except Exception as e:
            # Catch-all for any other unexpected errors
            if not isinstance(e, (RateLimitError, Exception)):
                print(f"\n❌ [UNEXPECTED ERROR]", file=sys.stderr)
                print(f"   URL: {method.upper()} {full_url}", file=sys.stderr)
                print(f"   Error: {type(e).__name__}: {str(e)}", file=sys.stderr)
                print(f"   Traceback:", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
            raise

    async def get_scenario_definition(
        self,
        scenario_id: int,
        _retry_count: int = 0,
        _max_retries: int = 3
    ) -> Optional[ScenarioDefinition]:
        """
        Get scenario definition with auth config references (zero credential exposure).

        Returns scenario definition as specified in the MVP spec:
        - Contains ${auth_config_id} placeholders instead of resolved tokens
        - Includes auth_configs with metadata for local resolution
        """
        try:
            data = await self._request('GET', f'/scenario/{scenario_id}/definition')

            # Skip scenarios without validations
            if not data.get('validations'):
                print(f"⚠️  Scenario {scenario_id} has no validations")
                return None

            return ScenarioDefinition.from_api_response(data)

        except RateLimitError as e:
            # Check if we've exceeded max retries
            if _retry_count >= _max_retries:
                print(f"\n❌ Rate limit exceeded for scenario {scenario_id} after {_max_retries} retries", file=sys.stderr)
                return None

            # Calculate backoff
            import random
            base_wait = e.retry_after if hasattr(e, 'retry_after') else 60
            wait_time = min(base_wait * (2 ** _retry_count) + random.uniform(0, 3), 180)

            print(f"\n⏱️  Rate limit hit fetching scenario {scenario_id}, retrying in {wait_time:.1f}s...", file=sys.stderr)
            await asyncio.sleep(wait_time)

            return await self.get_scenario_definition(
                scenario_id=scenario_id,
                _retry_count=_retry_count + 1,
                _max_retries=_max_retries
            )

        except Exception as e:
            print(f"\n⚠️  Failed to fetch scenario {scenario_id}", file=sys.stderr)
            print(f"   {str(e)}", file=sys.stderr)
            return None

    async def get_endpoint_scenarios(self, endpoint_id: int, only_with_validations: bool = False) -> List[ScenarioDefinition]:
        """Get all scenarios for an endpoint, optionally filtering to only those with validations."""
        try:
            params = {}
            if only_with_validations:
                params['only_with_validations'] = 'true'

            data = await self._request('GET', f'/endpoints/{endpoint_id}/scenarios', params=params)

            # Fetch full definitions for each scenario
            scenarios = []
            for scenario_info in data.get('scenarios', []):
                scenario_def = await self.get_scenario_definition(scenario_info['id'])
                if scenario_def:
                    scenarios.append(scenario_def)

            return scenarios

        except Exception as e:
            print(f"\n⚠️  Failed to fetch scenarios for endpoint {endpoint_id}", file=sys.stderr)
            print(f"   {str(e)}", file=sys.stderr)
            return []

    async def get_system_scenarios(self, system_id: int, only_with_validations: bool = False) -> tuple[List[ScenarioDefinition], Dict[str, Any]]:
        """
        Get all scenarios for a system, optionally filtering to only those with validations.

        Returns:
            tuple[List[ScenarioDefinition], Dict[str, Any]]: (scenarios, endpoint_metadata)
                - scenarios: List of scenario definitions
                - endpoint_metadata: Dict mapping endpoint_id to endpoint info (method, path, scenario_count)
        """
        try:
            params = {}
            if only_with_validations:
                params['only_with_validations'] = 'true'

            data = await self._request('GET', f'/system/{system_id}/scenarios', params=params)

            # Build endpoint metadata for display
            endpoint_metadata = {}
            for endpoint_info in data.get('endpoints', []):
                endpoint_metadata[endpoint_info['endpoint_id']] = {
                    'method': endpoint_info['method'],
                    'path': endpoint_info['path'],
                    'scenario_count': endpoint_info['scenario_count']
                }

            # Fetch full definitions for each scenario (preserving endpoint grouping)
            scenarios = []
            for endpoint_info in data.get('endpoints', []):
                for scenario_info in endpoint_info.get('scenarios', []):
                    scenario_def = await self.get_scenario_definition(scenario_info['id'])
                    if scenario_def:
                        # Attach endpoint metadata to scenario for display purposes
                        scenario_def._endpoint_method = endpoint_info['method']
                        scenario_def._endpoint_path = endpoint_info['path']
                        scenarios.append(scenario_def)

            return scenarios, endpoint_metadata

        except Exception as e:
            print(f"\n⚠️  Failed to fetch scenarios for system {system_id}", file=sys.stderr)
            print(f"   {str(e)}", file=sys.stderr)
            return [], {}

    async def submit_scenario_results(
        self,
        scenario_id: int,
        execution_data: Dict[str, Any],
        record_run: bool = True,
        increment_usage: bool = True,
        _retry_count: int = 0,
        _max_retries: int = 5
    ) -> Dict[str, Any]:
        """
        Submit scenario execution results for validation and persistence.

        Supports both successful executions and error cases as per MVP spec.
        Implements exponential backoff retry logic for rate limiting.

        Args:
            scenario_id: Scenario ID
            execution_data: Execution results
            record_run: Whether to record the run in history
            increment_usage: Whether to increment usage counters
            _retry_count: Internal retry counter
            _max_retries: Maximum number of retries (default: 5)
        """
        try:
            params = {}
            if record_run:
                params['record_run'] = 'true'
            if increment_usage:
                params['increment_usage'] = 'true'

            return await self._request(
                'POST',
                f'/scenario/{scenario_id}/check-validations',
                params=params,
                json=execution_data
            )

        except RateLimitError as e:
            # Check if we've exceeded max retries
            if _retry_count >= _max_retries:
                print(f"\n❌ [RATE LIMIT EXCEEDED]", file=sys.stderr)
                print(f"   Scenario: {scenario_id}", file=sys.stderr)
                print(f"   Max retries ({_max_retries}) exceeded", file=sys.stderr)
                print(f"   Suggestion: Reduce concurrency with SMARTTEST_CONCURRENCY=1 or wait before retrying", file=sys.stderr)
                # Return fallback result instead of failing completely
                return {
                    'scenario_id': scenario_id,
                    'execution_status': 'submission_error',
                    'validations': [],
                    'summary': {'passed': 0, 'failed': 0, 'submission_error': True},
                    'error': 'Rate limit exceeded after maximum retries'
                }

            # Calculate backoff with jitter to avoid thundering herd
            import random
            base_wait = e.retry_after if hasattr(e, 'retry_after') else 60
            # Exponential backoff: base * 2^retry_count with jitter
            wait_time = min(base_wait * (2 ** _retry_count) + random.uniform(0, 5), 300)  # Max 5 minutes

            print(f"\n⏱️  Rate limit hit for scenario {scenario_id}", file=sys.stderr)
            print(f"   Retry {_retry_count + 1}/{_max_retries} in {wait_time:.1f}s...", file=sys.stderr)

            await asyncio.sleep(wait_time)

            # Retry with incremented counter
            return await self.submit_scenario_results(
                scenario_id=scenario_id,
                execution_data=execution_data,
                record_run=record_run,
                increment_usage=increment_usage,
                _retry_count=_retry_count + 1,
                _max_retries=_max_retries
            )

        except Exception as e:
            print(f"\n⚠️  Failed to submit results for scenario {scenario_id}", file=sys.stderr)
            print(f"   Error: {str(e)}", file=sys.stderr)
            print(f"   Continuing with graceful degradation (scenario executed but validation not checked)", file=sys.stderr)
            # Return a fallback result for graceful degradation
            return {
                'scenario_id': scenario_id,
                'execution_status': 'submission_error',
                'validations': [],
                'summary': {'passed': 0, 'failed': 0, 'submission_error': True},
                'error': str(e)
            }