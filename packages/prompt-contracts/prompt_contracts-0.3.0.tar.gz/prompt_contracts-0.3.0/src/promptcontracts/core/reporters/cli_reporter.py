"""CLI reporter with rich formatting."""

from typing import Any

from rich.console import Console


class CLIReporter:
    """Pretty CLI reporter using rich."""

    def __init__(self):
        self.console = Console()

    def report(self, results: dict[str, Any], output_path: str = None):
        """
        Print results to CLI.

        Args:
            results: Results from ContractRunner
            output_path: Ignored for CLI reporter
        """
        for target_result in results.get("targets", []):
            self._report_target(target_result)

        # Show artifact directory if saved
        artifact_dir = results.get("artifact_base_dir")
        if artifact_dir:
            self.console.print()
            self.console.print(f"[bold cyan]📁 Artifacts saved to:[/bold cyan] {artifact_dir}")
            self.console.print()

    def _report_target(self, target_result: dict[str, Any]):
        """Report results for a single target."""
        target = target_result["target"]
        target_id = target_result.get("target_id", f"{target.get('type')}:{target.get('model')}")
        execution = target_result.get("execution", {})

        effective_mode = execution.get("effective_mode", "unknown")
        is_nonenforceable = execution.get("is_nonenforceable", False)

        self.console.print()
        self.console.print(f"[bold cyan]TARGET {target_id}[/bold cyan]")

        # Show execution mode
        mode_str = f"mode: {effective_mode}"
        if is_nonenforceable:
            mode_str += " [yellow](NONENFORCEABLE - schema not supported)[/yellow]"
        self.console.print(f"  {mode_str}")
        self.console.print()

        # Print fixture results
        for fixture_result in target_result.get("fixtures", []):
            self._print_fixture(fixture_result)

        # Print summary
        self._print_summary(target_result.get("summary", {}))

    def _print_fixture(self, fixture_result: dict[str, Any]):
        """Print a single fixture result."""
        fixture_id = fixture_result.get("fixture_id")
        latency_ms = fixture_result.get("latency_ms")
        mean_latency_ms = fixture_result.get("mean_latency_ms", latency_ms)
        status = fixture_result.get("status", "UNKNOWN")
        sampling_meta = fixture_result.get("sampling_metadata", {})
        repair_ledger = fixture_result.get("repair_ledger", [])

        # Status color
        status_colors = {
            "PASS": "green",
            "REPAIRED": "yellow",
            "FAIL": "red",
            "NONENFORCEABLE": "yellow",
        }
        status_color = status_colors.get(status, "white")

        # Header with sampling info
        n_samples = sampling_meta.get("n_samples", 1)
        if n_samples > 1:
            pass_rate = sampling_meta.get("pass_rate", 0.0)
            ci = sampling_meta.get("confidence_interval")
            header = f"[bold]Fixture:[/bold] {fixture_id} (n={n_samples}, mean latency: {mean_latency_ms:.1f}ms, pass rate: {pass_rate:.2f}"
            if ci:
                header += f" CI:[{ci[0]:.2f}, {ci[1]:.2f}]"
            header += f", status: [{status_color}]{status}[/{status_color}])"
        else:
            header = f"[bold]Fixture:[/bold] {fixture_id} (latency: {latency_ms}ms, status: [{status_color}]{status}[/{status_color}])"

        self.console.print(header)

        # Show repair ledger if any
        if repair_ledger:
            repairs_applied = [r.get("steps_applied", []) for r in repair_ledger]
            all_steps = [step for steps in repairs_applied for step in steps]
            if all_steps:
                self.console.print(f"  [dim]Repairs applied: {', '.join(set(all_steps))}[/dim]")

        # Print checks
        for check in fixture_result.get("checks", []):
            self._print_check(check)

        # Show artifact path if available
        artifact_path = fixture_result.get("artifact_path")
        if artifact_path:
            self.console.print(f"  [dim]Artifacts: {artifact_path}[/dim]")

        self.console.print()

    def _print_check(self, check: dict[str, Any]):
        """Print a single check result."""
        passed = check.get("passed")
        check_type = check.get("type")
        message = check.get("message")

        status_symbol = "✓" if passed else "✗"
        status_text = "PASS" if passed else "FAIL"
        status_color = "green" if passed else "red"

        self.console.print(
            f"  [{status_color}]{status_symbol} {status_text}[/{status_color}] | {check_type}"
        )
        self.console.print(f"         {message}")

    def _print_summary(self, summary: dict[str, Any]):
        """Print summary."""
        total = summary.get("total_checks", 0)
        passed = summary.get("passed_checks", 0)
        status = summary.get("status", "UNKNOWN")
        fixture_statuses = summary.get("fixture_statuses", {})

        status_colors = {
            "GREEN": "green",
            "YELLOW": "yellow",
            "RED": "red",
        }
        status_color = status_colors.get(status, "white")

        self.console.print("=" * 60)
        summary_text = f"[bold]Summary:[/bold] {passed}/{total} checks passed"

        # Add fixture status breakdown
        if fixture_statuses:
            breakdown = []
            if fixture_statuses.get("PASS", 0) > 0:
                breakdown.append(f"[green]{fixture_statuses['PASS']} PASS[/green]")
            if fixture_statuses.get("REPAIRED", 0) > 0:
                breakdown.append(f"[yellow]{fixture_statuses['REPAIRED']} REPAIRED[/yellow]")
            if fixture_statuses.get("FAIL", 0) > 0:
                breakdown.append(f"[red]{fixture_statuses['FAIL']} FAIL[/red]")
            if fixture_statuses.get("NONENFORCEABLE", 0) > 0:
                breakdown.append(
                    f"[yellow]{fixture_statuses['NONENFORCEABLE']} NONENFORCEABLE[/yellow]"
                )

            if breakdown:
                summary_text += f" ({', '.join(breakdown)})"

        summary_text += f" — status: [{status_color}]{status}[/{status_color}]"

        self.console.print(summary_text)
        self.console.print("=" * 60)
        self.console.print()
