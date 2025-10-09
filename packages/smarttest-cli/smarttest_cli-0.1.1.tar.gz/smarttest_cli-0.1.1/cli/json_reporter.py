"""
JSON reporter for CI/CD integration and programmatic parsing.

Generates machine-readable JSON output with complete test results,
making it easy for CI systems to parse and display test metrics.
"""

from typing import List, Dict, Any
from collections import defaultdict

from .models import ScenarioResult, ExecutionSummary


class JsonReporter:
    """
    JSON reporter for CI/CD integration.

    Generates structured JSON output containing:
    - Summary statistics (total, passed, failed, success rate)
    - Endpoint-grouped results
    - Individual scenario details
    - Validation failures and error messages
    """

    def generate_report(self, results: List[ScenarioResult], summary: ExecutionSummary) -> Dict[str, Any]:
        """
        Generate JSON report structure.

        Args:
            results: List of scenario execution results
            summary: Execution summary with aggregated statistics

        Returns:
            Dictionary that can be serialized to JSON with all test results
        """
        # Build endpoint grouping (if metadata available)
        endpoints = defaultdict(lambda: {
            "scenarios": [],
            "passed": 0,
            "failed": 0,
            "errors": 0
        })

        for result in results:
            # Determine endpoint key
            if hasattr(result, '_endpoint_method') and hasattr(result, '_endpoint_path'):
                endpoint_key = f"{result._endpoint_method} {result._endpoint_path}"
            else:
                endpoint_key = "_ungrouped"

            # Build scenario result
            scenario_data = self._build_scenario_data(result)
            endpoints[endpoint_key]["scenarios"].append(scenario_data)

            # Update endpoint stats
            if result.passed:
                endpoints[endpoint_key]["passed"] += 1
            elif result.failed:
                endpoints[endpoint_key]["failed"] += 1
            elif result.error:
                endpoints[endpoint_key]["errors"] += 1

        # Build final report structure
        report = {
            "summary": {
                "total": summary.total,
                "passed": summary.passed,
                "failed": summary.failed,
                "errors": summary.errors,
                "success_rate": round(summary.success_rate, 2),
                "duration_seconds": round(summary.execution_time_seconds, 2)
            },
            "endpoints": self._build_endpoint_list(endpoints),
            "results": self._build_results_list(results)
        }

        return report

    def _build_scenario_data(self, result: ScenarioResult) -> Dict[str, Any]:
        """Build detailed scenario data for JSON output."""
        scenario_data = {
            "scenario_id": result.scenario_id,
            "scenario_name": result.scenario_name,
            "status": self._get_status_string(result),
            "execution_status": result.execution_status.value,
            "http_status": result.http_status,
            "response_time_ms": result.response_time_ms,
            "run_id": result.run_id
        }

        # Add validation results if present
        if result.validation_results:
            scenario_data["validations"] = [
                {
                    "validation_id": v.validation_id,
                    "name": v.name,
                    "passed": v.passed,
                    "details": v.details
                }
                for v in result.validation_results
            ]

        # Add error details if present
        if result.error_details:
            scenario_data["error"] = {
                "type": result.error_details.get('error_type'),
                "message": result.error_details.get('message')
            }

        # Add validation failures if present
        if result.failed:
            failed_validations = [v for v in result.validation_results if not v.passed]
            scenario_data["validation_failures"] = [
                {
                    "validation": v.name,
                    "message": v.details.get('message') if v.details else "Validation failed"
                }
                for v in failed_validations
            ]

        return scenario_data

    def _build_endpoint_list(self, endpoints: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Build endpoint list with aggregated statistics."""
        return [
            {
                "endpoint": endpoint_key if endpoint_key != "_ungrouped" else "Unknown",
                "total": len(endpoint_data["scenarios"]),
                "passed": endpoint_data["passed"],
                "failed": endpoint_data["failed"],
                "errors": endpoint_data["errors"],
                "scenarios": endpoint_data["scenarios"]
            }
            for endpoint_key, endpoint_data in endpoints.items()
        ]

    def _build_results_list(self, results: List[ScenarioResult]) -> List[Dict[str, Any]]:
        """Build simplified results list for quick scanning."""
        return [
            {
                "scenario_id": r.scenario_id,
                "scenario_name": r.scenario_name,
                "endpoint": f"{r._endpoint_method} {r._endpoint_path}" if hasattr(r, '_endpoint_method') else None,
                "status": self._get_status_string(r),
                "http_status": r.http_status,
                "response_time_ms": r.response_time_ms
            }
            for r in results
        ]

    def _get_status_string(self, result: ScenarioResult) -> str:
        """Get human-readable status string."""
        if result.passed:
            return "passed"
        elif result.failed:
            return "failed"
        elif result.error:
            return "error"
        else:
            return "unknown"
