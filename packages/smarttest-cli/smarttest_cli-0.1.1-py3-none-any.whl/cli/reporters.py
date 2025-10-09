"""
Progress reporting and output formatting for SmartTest CLI.

Implements real-time progress reporting and various output formats
as specified in the MVP requirements.
"""

import time
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.progress import (
    Progress, TaskID, BarColumn, TextColumn, TimeRemainingColumn,
    SpinnerColumn, MofNCompleteColumn
)
from rich.table import Table
from rich.panel import Panel

from .models import ScenarioResult, ExecutionSummary, ExecutionStatus

class BaseReporter(ABC):
    """Base class for all reporters."""

    @abstractmethod
    def start_execution(self, total_scenarios: int):
        """Called when execution starts."""
        pass

    @abstractmethod
    def report_scenario_start(self, scenario_id: int, scenario_name: str):
        """Called when a scenario starts executing."""
        pass

    @abstractmethod
    def report_scenario_complete(self, result: ScenarioResult):
        """Called when a scenario completes."""
        pass

    @abstractmethod
    def finish_execution(self, results: List[ScenarioResult], summary: ExecutionSummary):
        """Called when all scenarios complete."""
        pass

    @abstractmethod
    def report_interruption(self):
        """Called when execution is interrupted."""
        pass

class TerminalReporter(BaseReporter):
    """
    Rich terminal reporter with real-time progress updates.

    Provides the enhanced UX specified in the MVP with:
    - Real-time progress bar
    - Pass/fail/error counts
    - Detailed error reporting
    - Final summary with success rate
    """

    def __init__(self, console: Console):
        self.console = console
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
        self.start_time: float = 0
        self.completed_count: int = 0
        self.total_scenarios: int = 0

        # Track results for final reporting
        self.results: List[ScenarioResult] = []

    def start_execution(self, total_scenarios: int):
        """Initialize progress tracking."""
        self.total_scenarios = total_scenarios
        self.start_time = time.time()
        self.completed_count = 0

        # Create progress bar with detailed columns
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=self.console,
        )

        self.progress.start()
        self.task_id = self.progress.add_task(
            "⚡ Executing scenarios...",
            total=total_scenarios
        )

        self.console.print(f"🔍 Found {total_scenarios} scenarios with validations")

    def report_scenario_start(self, scenario_id: int, scenario_name: str):
        """Report when a scenario starts (for debug visibility)."""
        # In production, we might not show individual starts to avoid spam
        # But useful for debugging concurrent execution
        pass

    def report_scenario_complete(self, result: ScenarioResult):
        """Update progress when scenario completes."""
        self.results.append(result)
        self.completed_count += 1

        if self.progress and self.task_id:
            # Update progress bar
            self.progress.update(self.task_id, advance=1)

            # Update description with current stats
            passed = sum(1 for r in self.results if r.passed)
            failed = sum(1 for r in self.results if r.failed)
            errors = sum(1 for r in self.results if r.error)

            description = f"⚡ Executing scenarios... ✅ {passed} passed, ❌ {failed} failed, ⚠️  {errors} errors"
            self.progress.update(self.task_id, description=description)

    def finish_execution(self, results: List[ScenarioResult], summary: ExecutionSummary):
        """Generate final report."""
        if self.progress:
            self.progress.stop()

        # Generate detailed final report
        self._generate_final_report(results, summary)

    def report_interruption(self):
        """Handle execution interruption."""
        if self.progress:
            self.progress.stop()

        self.console.print("\n⚠️  [yellow]Execution interrupted by user[/yellow]")

        if self.results:
            self.console.print(f"Partial results: {len(self.results)}/{self.total_scenarios} scenarios completed")

    def _generate_final_report(self, results: List[ScenarioResult], summary: ExecutionSummary):
        """Generate comprehensive final report matching MVP spec."""

        # Group results by endpoint (if endpoint metadata is available)
        from collections import defaultdict
        endpoint_groups = defaultdict(list)
        has_endpoint_metadata = False

        for result in results:
            # Check if result has endpoint metadata attached
            if hasattr(result, '_endpoint_method') and hasattr(result, '_endpoint_path'):
                endpoint_key = f"{result._endpoint_method} {result._endpoint_path}"
                endpoint_groups[endpoint_key].append(result)
                has_endpoint_metadata = True
            else:
                endpoint_groups['_ungrouped'].append(result)

        # Display grouped results
        if has_endpoint_metadata:
            self.console.print(f"\n[bold]Results by Endpoint:[/bold]")
            for endpoint_key, endpoint_results in endpoint_groups.items():
                if endpoint_key == '_ungrouped':
                    continue

                passed_count = sum(1 for r in endpoint_results if r.passed)
                failed_count = sum(1 for r in endpoint_results if r.failed)
                error_count = sum(1 for r in endpoint_results if r.error)

                # Endpoint header
                status_emoji = "✅" if failed_count == 0 and error_count == 0 else "❌"
                self.console.print(f"\n{status_emoji} [cyan]{endpoint_key}[/cyan] → {passed_count}/{len(endpoint_results)} passed")

                # Show failed scenarios under this endpoint
                for result in endpoint_results:
                    if result.failed:
                        failed_validations = [v for v in result.validation_results if not v.passed]
                        failure_details = ", ".join([
                            f"{v.name}: {v.details.get('message', 'Failed')}" if v.details else f"{v.name}: Failed"
                            for v in failed_validations
                        ])
                        self.console.print(f"     ↳ [red]{result.scenario_name}[/red]: {failure_details}")
                    elif result.error:
                        error_msg = result.error_details.get('message', 'Unknown error') if result.error_details else 'Unknown error'
                        self.console.print(f"     ↳ [yellow]{result.scenario_name}[/yellow]: {error_msg}")

        # Overall summary
        self.console.print(f"\n[bold]Overall Summary:[/bold]")

        # Success/failure summary with colors
        if summary.passed > 0:
            self.console.print(f"✅ [green]{summary.passed} passed[/green]")

        if summary.failed > 0:
            self.console.print(f"❌ [red]{summary.failed} failed (validation errors)[/red]")

        if summary.errors > 0:
            self.console.print(f"⚠️  [yellow]{summary.errors} errors (network/auth issues)[/yellow]")

        # Legacy flat view (if no endpoint metadata)
        if not has_endpoint_metadata:
            failed_scenarios = [r for r in results if r.failed]
            error_scenarios = [r for r in results if r.error]

            if failed_scenarios:
                self.console.print(f"\n[bold red]Failed scenarios:[/bold red]")
                for result in failed_scenarios:
                    failed_validations = [v for v in result.validation_results if not v.passed]
                    failure_details = ", ".join([
                        f"{v.name}: {v.details.get('message', 'Validation failed')}"
                        if v.details else f"{v.name}: Validation failed"
                        for v in failed_validations
                    ])
                    self.console.print(f"  - [red]{result.scenario_name}[/red]: {failure_details}")

            if error_scenarios:
                self.console.print(f"\n[bold yellow]Error scenarios:[/bold yellow]")
                for result in error_scenarios:
                    error_msg = "Unknown error"
                    if result.error_details:
                        error_msg = result.error_details.get('message', 'Unknown error')

                    self.console.print(f"  - [yellow]{result.scenario_name}[/yellow]: {error_msg}")

        # Final summary with timing and success rate
        self.console.print(f"\n[bold]Summary:[/bold] {summary.passed}/{summary.total} scenarios passed "
                          f"({summary.success_rate:.1f}% success rate)")

        if summary.execution_time_seconds > 0:
            self.console.print(f"Execution time: {summary.execution_time_seconds:.1f}s")

class JunitReporter:
    """
    JUnit XML reporter for CI integration.

    Generates XML reports compatible with standard CI systems
    as specified in the MVP requirements.
    """

    def generate_report(self, results: List[ScenarioResult], output_path: str):
        """Generate JUnit XML report file."""

        # Calculate summary stats
        total = len(results)
        failures = sum(1 for r in results if r.failed)
        errors = sum(1 for r in results if r.error)
        total_time = sum((r.response_time_ms or 0) / 1000.0 for r in results)

        # Create root testsuites element
        testsuites = ET.Element("testsuites")
        testsuites.set("name", "SmartTest")
        testsuites.set("tests", str(total))
        testsuites.set("failures", str(failures))
        testsuites.set("errors", str(errors))
        testsuites.set("time", f"{total_time:.3f}")

        # Create single testsuite (could be enhanced to group by system/endpoint)
        testsuite = ET.SubElement(testsuites, "testsuite")
        testsuite.set("name", "smarttest-scenarios")
        testsuite.set("tests", str(total))
        testsuite.set("failures", str(failures))
        testsuite.set("errors", str(errors))
        testsuite.set("time", f"{total_time:.3f}")

        # Add testcase for each scenario
        for result in results:
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", result.scenario_name)
            testcase.set("classname", f"scenario_{result.scenario_id}")

            if result.response_time_ms:
                testcase.set("time", f"{result.response_time_ms / 1000.0:.3f}")
            else:
                testcase.set("time", "0")

            # Add failure or error elements as appropriate
            if result.failed:
                # Validation failures
                failed_validations = [v for v in result.validation_results if not v.passed]
                failure_messages = []
                for validation in failed_validations:
                    if validation.details:
                        failure_messages.append(
                            f"{validation.name}: {validation.details.get('message', 'Validation failed')}"
                        )
                    else:
                        failure_messages.append(f"{validation.name}: Validation failed")

                failure = ET.SubElement(testcase, "failure")
                failure.set("message", "; ".join(failure_messages))
                failure.text = self._format_failure_details(result)

            elif result.error:
                # Execution errors (network, auth, etc.)
                error = ET.SubElement(testcase, "error")
                error_msg = "Unknown error"
                if result.error_details:
                    error_msg = result.error_details.get('message', 'Unknown error')

                error.set("message", error_msg)
                error.set("type", result.execution_status.value)
                error.text = self._format_error_details(result)

        # Write XML to file
        tree = ET.ElementTree(testsuites)
        ET.indent(tree, space="  ")  # Pretty formatting

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)

    def _format_failure_details(self, result: ScenarioResult) -> str:
        """Format detailed failure information for JUnit."""
        details = [f"Scenario: {result.scenario_name} (ID: {result.scenario_id})"]

        if result.http_status:
            details.append(f"HTTP Status: {result.http_status}")

        if result.response_time_ms:
            details.append(f"Response Time: {result.response_time_ms}ms")

        # Add validation details
        for validation in result.validation_results:
            if not validation.passed and validation.details:
                details.append(f"Validation '{validation.name}': {validation.details}")

        return "\\n".join(details)

    def _format_error_details(self, result: ScenarioResult) -> str:
        """Format detailed error information for JUnit."""
        details = [f"Scenario: {result.scenario_name} (ID: {result.scenario_id})"]
        details.append(f"Execution Status: {result.execution_status.value}")

        if result.response_time_ms:
            details.append(f"Response Time: {result.response_time_ms}ms")

        if result.error_details:
            details.append(f"Error Type: {result.error_details.get('error_type', 'Unknown')}")
            details.append(f"Error Message: {result.error_details.get('message', 'No details')}")

        return "\\n".join(details)