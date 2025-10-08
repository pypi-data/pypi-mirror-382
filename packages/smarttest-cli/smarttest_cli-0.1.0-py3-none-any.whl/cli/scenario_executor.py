"""
Scenario executor with concurrent execution and comprehensive error handling.

Implements the core execution logic as specified in the MVP:
- Fixed concurrency limit (5 concurrent scenarios)
- Continue-on-error execution (never stop due to individual failures)
- Real-time progress reporting
- Comprehensive error classification and handling
"""

import asyncio
import time
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

from .config import Config
from .api_client import ApiClient
from .http_executor import HttpExecutor
from .models import ScenarioDefinition, ScenarioResult, ExecutionSummary, ExecutionStatus
from .reporters import BaseReporter

class ScenarioExecutor:
    """
    Orchestrates the execution of multiple test scenarios with:
    - Concurrent execution (max 5 as per MVP spec)
    - Continue-on-error behavior
    - Real-time progress reporting
    - Comprehensive error handling
    """

    def __init__(self, config: Config, api_client: ApiClient):
        self.config = config
        self.api_client = api_client
        self.http_executor = HttpExecutor(config)

    async def close(self):
        """Clean up resources."""
        await self.http_executor.close()

    async def execute_scenarios(
        self,
        scenarios: List[ScenarioDefinition],
        reporter: BaseReporter
    ) -> List[ScenarioResult]:
        """
        Execute scenarios concurrently with progress reporting.

        Key behaviors per MVP specification:
        - Fixed concurrency limit of 5 (configurable via config)
        - Continue-on-error: individual scenario failures don't stop execution
        - Real-time progress updates
        - Comprehensive result collection
        """

        if not scenarios:
            return []

        start_time = time.time()
        results = []

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.config.concurrency)

        # Start progress reporting
        reporter.start_execution(total_scenarios=len(scenarios))

        try:
            # Create tasks for all scenarios
            tasks = []
            for scenario in scenarios:
                task = asyncio.create_task(
                    self._execute_single_scenario_with_semaphore(
                        semaphore, scenario, reporter
                    )
                )
                tasks.append(task)

            # Wait for all scenarios to complete
            # Use return_when=ALL_COMPLETED to ensure we get all results
            completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for i, result in enumerate(completed_tasks):
                if isinstance(result, Exception):
                    # Create error result for task that raised an exception
                    scenario = scenarios[i]
                    error_result = ScenarioResult(
                        scenario_id=scenario.id,
                        scenario_name=scenario.name,
                        execution_status=ExecutionStatus.UNKNOWN_ERROR,
                        error_details={
                            'error_type': 'TaskException',
                            'message': str(result)
                        }
                    )
                    results.append(error_result)
                else:
                    results.append(result)

            # Generate execution summary
            execution_time = time.time() - start_time
            summary = self._generate_summary(results, execution_time)

            # Final progress report
            reporter.finish_execution(results, summary)

            return results

        except KeyboardInterrupt:
            # Handle graceful shutdown on Ctrl+C
            reporter.report_interruption()

            # Cancel pending tasks
            for task in tasks:
                if not task.done():
                    task.cancel()

            # Wait briefly for cancellation to complete
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                pass

            raise

        finally:
            await self.close()

    async def _execute_single_scenario_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        scenario: ScenarioDefinition,
        reporter: BaseReporter
    ) -> ScenarioResult:
        """
        Execute single scenario with concurrency control.

        The semaphore ensures we never exceed the configured concurrency limit.
        """

        async with semaphore:
            # Report scenario start
            reporter.report_scenario_start(scenario.id, scenario.name)

            try:
                # Execute the scenario
                result = await self.http_executor.execute_scenario(
                    scenario, self.api_client
                )

                # Report completion
                reporter.report_scenario_complete(result)

                return result

            except Exception as e:
                # Create error result for any unexpected exceptions
                error_result = ScenarioResult(
                    scenario_id=scenario.id,
                    scenario_name=scenario.name,
                    execution_status=ExecutionStatus.UNKNOWN_ERROR,
                    error_details={
                        'error_type': 'ExecutionException',
                        'message': str(e)
                    }
                )

                reporter.report_scenario_complete(error_result)
                return error_result

    def _generate_summary(
        self,
        results: List[ScenarioResult],
        execution_time: float
    ) -> ExecutionSummary:
        """Generate execution summary statistics."""

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if r.failed)
        errors = sum(1 for r in results if r.error)

        return ExecutionSummary(
            total=total,
            passed=passed,
            failed=failed,
            errors=errors,
            execution_time_seconds=execution_time
        )