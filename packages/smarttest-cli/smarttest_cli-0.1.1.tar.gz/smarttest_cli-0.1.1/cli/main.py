#!/usr/bin/env python3
"""
SmartTest CLI - Main entry point
Execute test scenarios inside customer networks with secure, enterprise-ready architecture.
"""

import sys
import asyncio
import json
from typing import Optional, List
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .api_client import ApiClient
from .scenario_executor import ScenarioExecutor
from .reporters import TerminalReporter, JunitReporter
from .json_reporter import JsonReporter

app = typer.Typer(
    name="smarttest",
    help="SmartTest CLI - Execute test scenarios with secure credential handling",
    add_completion=False
)
console = Console()

@app.command()
def main_command(
    scenario_id: Optional[int] = typer.Option(None, "--scenario-id", help="Run specific scenario by ID"),
    endpoint_id: Optional[int] = typer.Option(None, "--endpoint-id", help="Run all scenarios for an endpoint"),
    system_id: Optional[int] = typer.Option(None, "--system-id", help="Run all scenarios for a system"),
    config_file: Optional[str] = typer.Option(".smarttest.yml", "--config", help="Configuration file path"),
    report_file: Optional[str] = typer.Option(None, "--report", help="Generate JUnit XML report"),
    format: str = typer.Option("terminal", "--format", help="Output format: 'terminal' or 'json'"),
):
    """Execute test scenarios with zero-credential exposure security model."""

    # Validate arguments
    selection_count = sum(bool(x) for x in [scenario_id, endpoint_id, system_id])
    if selection_count != 1:
        console.print("❌ [red]Error: Must specify exactly one of --scenario-id, --endpoint-id, or --system-id[/red]")
        raise typer.Exit(1)

    # Validate format
    if format not in ["terminal", "json"]:
        console.print(f"❌ [red]Error: Invalid format '{format}'. Must be 'terminal' or 'json'[/red]")
        raise typer.Exit(1)

    # Load configuration
    try:
        config = Config.load(config_file)
    except Exception as e:
        console.print(f"❌ [red]Configuration error: {e}[/red]")
        raise typer.Exit(1)

    # Run the scenarios
    exit_code = asyncio.run(execute_scenarios(
        config=config,
        scenario_id=scenario_id,
        endpoint_id=endpoint_id,
        system_id=system_id,
        report_file=report_file,
        output_format=format
    ))

    raise typer.Exit(exit_code)

async def execute_scenarios(
    config: Config,
    scenario_id: Optional[int] = None,
    endpoint_id: Optional[int] = None,
    system_id: Optional[int] = None,
    report_file: Optional[str] = None,
    output_format: str = "terminal"
) -> int:
    """Main execution logic with error handling and reporting."""

    try:
        # Initialize components
        api_client = ApiClient(config)
        executor = ScenarioExecutor(config, api_client)

        # Use silent console for JSON mode
        use_console = console if output_format == "terminal" else Console(quiet=True, file=sys.stderr)
        reporter = TerminalReporter(use_console)

        # Discover scenarios
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=use_console,
            transient=True,
            disable=(output_format == "json")
        ) as progress:
            discovery_task = progress.add_task("🔍 Discovering scenarios...", total=None)

            endpoint_metadata = {}
            if scenario_id:
                scenarios = await api_client.get_scenario_definition(scenario_id)
                scenarios = [scenarios] if scenarios else []
            elif endpoint_id:
                scenarios = await api_client.get_endpoint_scenarios(endpoint_id, only_with_validations=True)
            elif system_id:
                scenarios, endpoint_metadata = await api_client.get_system_scenarios(system_id, only_with_validations=True)
            else:
                scenarios = []

            progress.update(discovery_task, completed=True)

        if not scenarios:
            if output_format == "json":
                # Output empty JSON result
                print(json.dumps({
                    "summary": {"total": 0, "passed": 0, "failed": 0, "errors": 0, "success_rate": 0.0, "duration_seconds": 0.0},
                    "endpoints": [],
                    "results": []
                }))
            else:
                use_console.print("❌ [yellow]No scenarios found with validations[/yellow]")
            return 1

        # Display discovery summary with endpoint grouping (terminal only)
        if output_format == "terminal":
            if system_id and endpoint_metadata:
                use_console.print(f"\n📋 [bold cyan]Discovered {len(scenarios)} scenarios across {len(endpoint_metadata)} endpoints:[/bold cyan]")
                for endpoint_id, info in endpoint_metadata.items():
                    use_console.print(f"   • [cyan]{info['method']}[/cyan] {info['path']} → [green]{info['scenario_count']} scenario(s)[/green]")
                use_console.print()  # Add blank line before execution
            else:
                use_console.print(f"🔍 Found {len(scenarios)} scenarios")

        # Execute scenarios
        results = await executor.execute_scenarios(scenarios, reporter)

        # Get execution summary from scenario executor
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if r.failed)
        errors = sum(1 for r in results if r.error)
        total = len(results)

        # Import ExecutionSummary for JSON reporter
        from .models import ExecutionSummary
        summary = ExecutionSummary(
            total=total,
            passed=passed,
            failed=failed,
            errors=errors,
            execution_time_seconds=0.0  # Will be calculated by reporter if needed
        )

        # Generate reports based on format
        if output_format == "json":
            # Generate JSON output
            json_reporter = JsonReporter()
            json_output = json_reporter.generate_report(results, summary)
            print(json.dumps(json_output, indent=2))
        else:
            # Terminal output already handled by TerminalReporter
            if report_file:
                junit_reporter = JunitReporter()
                junit_reporter.generate_report(results, report_file)
                use_console.print(f"📄 JUnit report generated: {report_file}")

            # Final summary
            if failed > 0 or errors > 0:
                use_console.print(f"\n❌ [red]{failed + errors} scenarios failed, {passed} passed[/red]")
            else:
                use_console.print(f"\n✅ [green]All {passed} scenarios passed[/green]")

        # Return exit code
        return 1 if (failed > 0 or errors > 0) else 0

    except KeyboardInterrupt:
        console.print("\n⚠️  [yellow]Execution interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n💥 [red]Fatal error: {e}[/red]")
        return 1

def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()