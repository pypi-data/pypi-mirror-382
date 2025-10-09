"""Check: Latency budget (p95)."""

from typing import Any

import numpy as np


def latency_budget_check(
    response_text: str, check_spec: dict[str, Any], all_latencies: list[int] = None, **kwargs
) -> tuple[bool, str, Any]:
    """
    Validate that p95 latency is within budget.

    This check is evaluated AFTER all fixtures have been processed.

    Args:
        response_text: Raw response text (not used directly)
        check_spec: Check configuration with 'p95_ms' integer
        all_latencies: List of all latency measurements in milliseconds

    Returns:
        (passed, message, p95_latency)
    """
    if all_latencies is None or len(all_latencies) == 0:
        return False, "No latency data available", None

    p95_threshold = check_spec.get("p95_ms", 0)

    # Calculate p95
    p95_actual = np.percentile(all_latencies, 95)

    if p95_actual <= p95_threshold:
        return True, f"p95 latency {p95_actual:.0f}ms <= {p95_threshold}ms", p95_actual
    else:
        return False, f"p95 latency {p95_actual:.0f}ms > {p95_threshold}ms", p95_actual
