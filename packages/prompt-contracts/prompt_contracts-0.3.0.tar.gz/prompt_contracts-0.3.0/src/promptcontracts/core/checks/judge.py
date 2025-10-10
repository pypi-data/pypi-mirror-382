"""
LLM-as-judge check for prompt contracts.

Uses an LLM to evaluate response quality against criteria with budget tracking
and configurable pass/fail policies.
"""

from typing import Any, Literal

PassWhenPolicy = Literal["all", "majority", "any"]


def judge_check(response_text: str, check_spec: dict[str, Any], **kwargs) -> tuple[bool, str]:
    """
    Use an LLM to judge response quality.

    Args:
        response_text: Response text to evaluate
        check_spec: Check specification with:
            - 'criteria': Evaluation criteria/prompt
            - 'pass_when': Policy for passing ("all", "majority", "any")
            - 'budget': Optional token/latency budget
        **kwargs: Must include 'judge_adapter'

    Returns:
        Tuple of (passed, message)
    """
    criteria = check_spec.get("criteria")
    pass_when = check_spec.get("pass_when", "all")
    budget = check_spec.get("budget", {})
    judge_adapter = kwargs.get("judge_adapter")

    if not criteria:
        return False, "No criteria specified for judge check"

    if not judge_adapter:
        return False, "Judge check requires judge_adapter in kwargs"

    try:
        # Build judge prompt
        judge_prompt = _build_judge_prompt(criteria, response_text)

        # Get judgment
        judgment_result = judge_adapter.judge(
            prompt=judge_prompt,
            budget=budget,
        )

        # Extract verdict
        verdict = judgment_result.get("verdict", False)
        explanation = judgment_result.get("explanation", "No explanation provided")
        tokens_used = judgment_result.get("tokens_used", 0)
        latency_ms = judgment_result.get("latency_ms", 0)

        # Check budget compliance
        budget_ok = _check_budget(budget, tokens_used, latency_ms)
        if not budget_ok:
            return (
                False,
                f"Judge exceeded budget: {tokens_used} tokens, {latency_ms}ms",
            )

        # Apply pass_when policy
        passed = _apply_pass_when_policy(verdict, pass_when)

        if passed:
            return True, f"Judge passed: {explanation} ({tokens_used} tokens)"
        else:
            return False, f"Judge failed: {explanation} ({tokens_used} tokens)"

    except Exception as e:
        return False, f"Judge check failed with error: {e}"


def _build_judge_prompt(criteria: str, response: str) -> str:
    """
    Build the judge evaluation prompt.

    Args:
        criteria: Evaluation criteria
        response: Response to evaluate

    Returns:
        Judge prompt
    """
    return f"""You are an expert evaluator. Evaluate the following response against the criteria.

CRITERIA:
{criteria}

RESPONSE TO EVALUATE:
{response}

Provide your evaluation in the following format:
VERDICT: [PASS or FAIL]
EXPLANATION: [Your detailed explanation]
"""


def _apply_pass_when_policy(verdict: bool, policy: PassWhenPolicy) -> bool:
    """
    Apply the pass_when policy to verdict.

    Args:
        verdict: Boolean verdict from judge
        policy: Pass policy

    Returns:
        Final pass/fail decision
    """
    # For single verdict, all policies are equivalent
    # In v0.3.1 we could extend this for multi-judge scenarios
    return verdict


def _check_budget(budget: dict[str, Any], tokens_used: int, latency_ms: float) -> bool:
    """
    Check if resource usage is within budget.

    Args:
        budget: Budget specification
        tokens_used: Tokens consumed
        latency_ms: Latency in milliseconds

    Returns:
        True if within budget
    """
    max_tokens = budget.get("max_tokens")
    max_latency_ms = budget.get("max_latency_ms")

    if max_tokens is not None and tokens_used > max_tokens:
        return False

    if max_latency_ms is not None and latency_ms > max_latency_ms:
        return False

    return True
