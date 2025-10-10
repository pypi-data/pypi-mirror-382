"""
Probabilistic sampling and aggregation for prompt contracts.

Provides N-sampling with configurable seeds, aggregation policies,
and bootstrap confidence intervals for statistical validation.
"""

import random
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

AggregationPolicy = Literal["majority", "all", "any", "first"]


@dataclass
class SamplingConfig:
    """Configuration for N-sampling."""

    n: int = 1
    seed: int | None = None
    aggregation: AggregationPolicy = "first"
    bootstrap_samples: int = 1000
    confidence_level: float = 0.95


@dataclass
class SampleResult:
    """Result of a single sample."""

    sample_id: int
    output: str
    parsed: Any
    latency_ms: float
    checks_passed: bool
    check_results: list[dict[str, Any]]


@dataclass
class AggregatedResult:
    """Aggregated result from N samples."""

    samples: list[SampleResult]
    aggregation_policy: AggregationPolicy
    selected_output: str
    selected_parsed: Any
    all_passed: bool
    pass_rate: float
    confidence_interval: tuple[float, float] | None
    total_latency_ms: float
    mean_latency_ms: float
    aggregation_metadata: dict[str, Any]


class Sampler:
    """Handles N-sampling and aggregation for probabilistic contracts."""

    def __init__(self, config: SamplingConfig):
        """
        Initialize sampler with configuration.

        Args:
            config: Sampling configuration
        """
        self.config = config
        if config.seed is not None:
            random.seed(config.seed)
            np.random.seed(config.seed)

    def aggregate(self, samples: list[SampleResult]) -> AggregatedResult:
        """
        Aggregate multiple sample results according to policy.

        Args:
            samples: List of sample results

        Returns:
            Aggregated result with selected output and metadata
        """
        if not samples:
            raise ValueError("No samples to aggregate")

        policy = self.config.aggregation
        total_latency = sum(s.latency_ms for s in samples)
        mean_latency = total_latency / len(samples)
        pass_rate = sum(1 for s in samples if s.checks_passed) / len(samples)

        # Compute confidence interval if requested
        ci = None
        if self.config.bootstrap_samples > 0 and len(samples) > 1:
            ci = self._bootstrap_ci(
                [1 if s.checks_passed else 0 for s in samples],
                self.config.bootstrap_samples,
                self.config.confidence_level,
            )

        metadata: dict[str, Any] = {"n_samples": len(samples)}

        # Select output based on policy
        if policy == "first":
            selected = samples[0]
            all_passed = selected.checks_passed
            metadata["policy_detail"] = "Selected first sample"

        elif policy == "majority":
            # Majority vote on outputs
            output_counts = Counter(s.output for s in samples)
            most_common_output, count = output_counts.most_common(1)[0]
            metadata["majority_count"] = count
            metadata["majority_fraction"] = count / len(samples)

            # Find first sample with majority output
            selected = next(s for s in samples if s.output == most_common_output)
            all_passed = pass_rate > 0.5
            metadata["policy_detail"] = f"Majority vote: {count}/{len(samples)}"

        elif policy == "all":
            # All samples must pass
            all_passed = all(s.checks_passed for s in samples)
            # Select first passing sample, or first sample if none pass
            passing = [s for s in samples if s.checks_passed]
            selected = passing[0] if passing else samples[0]
            metadata["policy_detail"] = f"All must pass: {all_passed}"

        elif policy == "any":
            # At least one sample must pass
            all_passed = any(s.checks_passed for s in samples)
            # Select first passing sample, or first sample if none pass
            passing = [s for s in samples if s.checks_passed]
            selected = passing[0] if passing else samples[0]
            metadata["policy_detail"] = f"Any must pass: {all_passed}"

        else:
            raise ValueError(f"Unknown aggregation policy: {policy}")

        return AggregatedResult(
            samples=samples,
            aggregation_policy=policy,
            selected_output=selected.output,
            selected_parsed=selected.parsed,
            all_passed=all_passed,
            pass_rate=pass_rate,
            confidence_interval=ci,
            total_latency_ms=total_latency,
            mean_latency_ms=mean_latency,
            aggregation_metadata=metadata,
        )

    def _bootstrap_ci(
        self, data: list[int], n_bootstrap: int, confidence: float
    ) -> tuple[float, float]:
        """
        Compute bootstrap confidence interval for pass rate.

        Args:
            data: Binary data (1=pass, 0=fail)
            n_bootstrap: Number of bootstrap samples
            confidence: Confidence level (e.g., 0.95)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if not data:
            return (0.0, 0.0)

        bootstrap_means = []
        n = len(data)

        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=n, replace=True)
            bootstrap_means.append(np.mean(sample))

        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        lower = float(np.percentile(bootstrap_means, lower_percentile))
        upper = float(np.percentile(bootstrap_means, upper_percentile))

        return (lower, upper)

    def sample_n(self, generator_fn: Callable[[int], SampleResult]) -> AggregatedResult:
        """
        Run N samples using the provided generator function.

        Args:
            generator_fn: Function that takes sample_id and returns SampleResult

        Returns:
            Aggregated result
        """
        samples = []
        for i in range(self.config.n):
            sample = generator_fn(i)
            samples.append(sample)

        return self.aggregate(samples)


def create_sampler(
    n: int = 1,
    seed: int | None = None,
    aggregation: AggregationPolicy = "first",
    bootstrap_samples: int = 1000,
    confidence_level: float = 0.95,
) -> Sampler:
    """
    Create a sampler with the given configuration.

    Args:
        n: Number of samples to take
        seed: Random seed for reproducibility
        aggregation: Aggregation policy
        bootstrap_samples: Number of bootstrap samples for CI
        confidence_level: Confidence level for CI

    Returns:
        Configured Sampler instance
    """
    config = SamplingConfig(
        n=n,
        seed=seed,
        aggregation=aggregation,
        bootstrap_samples=bootstrap_samples,
        confidence_level=confidence_level,
    )
    return Sampler(config)
