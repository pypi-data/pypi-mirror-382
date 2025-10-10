"""
Metrics computation for prompt contract evaluation.

Computes key metrics including validation success, task accuracy,
repair rate, latency, overhead, and provider consistency.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ContractMetrics:
    """Comprehensive metrics for contract execution."""

    # Validation metrics
    validation_success: float  # Fraction of fixtures passing all checks
    total_fixtures: int
    passed_fixtures: int
    failed_fixtures: int
    repaired_fixtures: int

    # Task accuracy (requires gold labels)
    task_accuracy: float | None  # Exact match accuracy vs gold
    task_accuracy_count: int | None  # Number with gold labels

    # Repair metrics
    repair_rate: float  # Fraction of fixtures that needed repair
    avg_repairs_per_fixture: float

    # Latency metrics
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_latency_ms: float

    # Overhead metrics
    overhead_pct: float | None  # Overhead vs baseline (if available)
    baseline_mean_latency_ms: float | None

    # Provider consistency (multi-sample)
    provider_consistency: float | None  # Agreement rate across samples


class MetricsComputer:
    """Computes metrics from contract execution results."""

    def compute(
        self,
        results: dict[str, Any],
        gold_labels: dict[str, Any] | None = None,
        baseline_latencies: list[float] | None = None,
    ) -> ContractMetrics:
        """
        Compute comprehensive metrics from execution results.

        Args:
            results: Contract execution results
            gold_labels: Optional gold labels for task accuracy
            baseline_latencies: Optional baseline latencies for overhead

        Returns:
            Computed metrics
        """
        # Collect all fixtures from all targets
        all_fixtures = []
        all_latencies = []

        for target in results.get("targets", []):
            for fixture in target.get("fixtures", []):
                all_fixtures.append(fixture)
                all_latencies.append(fixture.get("latency_ms", 0))

        total = len(all_fixtures)
        if total == 0:
            return self._empty_metrics()

        # Count statuses
        passed = sum(1 for f in all_fixtures if f.get("status") == "PASS")
        failed = sum(1 for f in all_fixtures if f.get("status") == "FAIL")
        repaired = sum(1 for f in all_fixtures if f.get("status") == "REPAIRED")

        # Validation success
        validation_success = passed / total if total > 0 else 0.0

        # Repair metrics
        repair_rate = repaired / total if total > 0 else 0.0
        total_repairs = sum(f.get("retries_used", 0) for f in all_fixtures)
        avg_repairs = total_repairs / total if total > 0 else 0.0

        # Task accuracy (if gold labels provided)
        task_accuracy = None
        task_accuracy_count = None
        if gold_labels:
            task_accuracy, task_accuracy_count = self._compute_task_accuracy(
                all_fixtures, gold_labels
            )

        # Latency metrics
        latency_metrics = self._compute_latency_metrics(all_latencies)

        # Overhead (if baseline provided)
        overhead_pct = None
        baseline_mean = None
        if baseline_latencies:
            baseline_mean = sum(baseline_latencies) / len(baseline_latencies)
            overhead_pct = (latency_metrics["mean"] - baseline_mean) / baseline_mean * 100

        # Provider consistency (from sampling metadata if available)
        provider_consistency = self._compute_provider_consistency(results)

        return ContractMetrics(
            validation_success=validation_success,
            total_fixtures=total,
            passed_fixtures=passed,
            failed_fixtures=failed,
            repaired_fixtures=repaired,
            task_accuracy=task_accuracy,
            task_accuracy_count=task_accuracy_count,
            repair_rate=repair_rate,
            avg_repairs_per_fixture=avg_repairs,
            mean_latency_ms=latency_metrics["mean"],
            median_latency_ms=latency_metrics["median"],
            p95_latency_ms=latency_metrics["p95"],
            p99_latency_ms=latency_metrics["p99"],
            total_latency_ms=latency_metrics["total"],
            overhead_pct=overhead_pct,
            baseline_mean_latency_ms=baseline_mean,
            provider_consistency=provider_consistency,
        )

    def _empty_metrics(self) -> ContractMetrics:
        """Return empty metrics when no fixtures are available."""
        return ContractMetrics(
            validation_success=0.0,
            total_fixtures=0,
            passed_fixtures=0,
            failed_fixtures=0,
            repaired_fixtures=0,
            task_accuracy=None,
            task_accuracy_count=None,
            repair_rate=0.0,
            avg_repairs_per_fixture=0.0,
            mean_latency_ms=0.0,
            median_latency_ms=0.0,
            p95_latency_ms=0.0,
            p99_latency_ms=0.0,
            total_latency_ms=0.0,
            overhead_pct=None,
            baseline_mean_latency_ms=None,
            provider_consistency=None,
        )

    def _compute_task_accuracy(
        self, fixtures: list[dict[str, Any]], gold_labels: dict[str, Any]
    ) -> tuple[float, int]:
        """
        Compute task accuracy against gold labels.

        Args:
            fixtures: List of fixture results
            gold_labels: Dict mapping fixture_id to expected output

        Returns:
            Tuple of (accuracy, count_with_gold)
        """
        matches = 0
        count = 0

        for fixture in fixtures:
            fixture_id = fixture.get("fixture_id")
            if fixture_id not in gold_labels:
                continue

            count += 1
            # Get normalized output for comparison
            output = fixture.get("normalized_output", "").strip()
            expected = str(gold_labels[fixture_id]).strip()

            if output == expected:
                matches += 1

        accuracy = matches / count if count > 0 else 0.0
        return accuracy, count

    def _compute_latency_metrics(self, latencies: list[float]) -> dict[str, float]:
        """
        Compute latency percentiles.

        Args:
            latencies: List of latency values in ms

        Returns:
            Dict with mean, median, p95, p99, total
        """
        if not latencies:
            return {
                "mean": 0.0,
                "median": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "total": 0.0,
            }

        sorted_lat = sorted(latencies)
        n = len(sorted_lat)

        return {
            "mean": sum(sorted_lat) / n,
            "median": sorted_lat[n // 2],
            "p95": sorted_lat[int(n * 0.95)] if n > 1 else sorted_lat[0],
            "p99": sorted_lat[int(n * 0.99)] if n > 1 else sorted_lat[0],
            "total": sum(sorted_lat),
        }

    def _compute_provider_consistency(self, results: dict[str, Any]) -> float | None:
        """
        Compute provider consistency from sampling metadata.

        Args:
            results: Execution results

        Returns:
            Consistency score (0-1) or None if not applicable
        """
        # Look for sampling metadata in results
        for target in results.get("targets", []):
            for fixture in target.get("fixtures", []):
                sampling_meta = fixture.get("sampling_metadata")
                if sampling_meta and "samples" in sampling_meta:
                    samples = sampling_meta["samples"]
                    if len(samples) > 1:
                        # Compute agreement: fraction of samples that match majority
                        outputs = [s.get("output", "") for s in samples]
                        from collections import Counter

                        counts = Counter(outputs)
                        most_common_count = counts.most_common(1)[0][1]
                        return most_common_count / len(samples)

        return None


def compute_metrics(
    results: dict[str, Any],
    gold_labels: dict[str, Any] | None = None,
    baseline_latencies: list[float] | None = None,
) -> ContractMetrics:
    """
    Convenience function to compute metrics.

    Args:
        results: Contract execution results
        gold_labels: Optional gold labels for task accuracy
        baseline_latencies: Optional baseline latencies for overhead

    Returns:
        Computed metrics
    """
    computer = MetricsComputer()
    return computer.compute(results, gold_labels, baseline_latencies)
