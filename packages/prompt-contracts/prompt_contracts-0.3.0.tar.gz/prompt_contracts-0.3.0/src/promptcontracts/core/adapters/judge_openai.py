"""
LLM-as-judge adapter using OpenAI.

Provides judge evaluation capabilities for semantic validation.
"""

import os
import re
import time
from typing import Any


class JudgeAdapter:
    """Base class for judge adapters."""

    def judge(self, prompt: str, budget: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Evaluate using LLM judge.

        Args:
            prompt: Judge prompt
            budget: Optional budget constraints

        Returns:
            Dict with verdict, explanation, tokens_used, latency_ms
        """
        raise NotImplementedError


class OpenAIJudgeAdapter(JudgeAdapter):
    """
    Judge adapter using OpenAI API.

    Requires: pip install openai
    """

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str | None = None):
        """
        Initialize OpenAI judge adapter.

        Args:
            model: OpenAI model name
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        try:
            from openai import OpenAI
        except ImportError as e:
            msg = "openai not installed. Install with: pip install openai"
            raise ImportError(msg) from e

        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            msg = "OpenAI API key not provided and OPENAI_API_KEY not set"
            raise ValueError(msg)

        self.client = OpenAI(api_key=self.api_key)

    def judge(self, prompt: str, budget: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Evaluate using OpenAI judge.

        Args:
            prompt: Judge prompt
            budget: Optional budget constraints

        Returns:
            Dict with verdict, explanation, tokens_used, latency_ms
        """
        budget = budget or {}
        max_tokens = budget.get("max_tokens", 500)

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert evaluator. " "Provide clear PASS/FAIL verdicts."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.0,
            )

            latency_ms = (time.time() - start_time) * 1000
            response_text = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0

            verdict, explanation = self._parse_verdict(response_text)

            return {
                "verdict": verdict,
                "explanation": explanation,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "raw_response": response_text,
            }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return {
                "verdict": False,
                "explanation": f"Judge error: {e}",
                "tokens_used": 0,
                "latency_ms": latency_ms,
                "raw_response": "",
            }

    def _parse_verdict(self, text: str) -> tuple[bool, str]:
        """
        Parse verdict from judge response.

        Args:
            text: Judge response text

        Returns:
            Tuple of (verdict, explanation)
        """
        verdict_match = re.search(r"VERDICT:\s*(PASS|FAIL)", text, re.IGNORECASE)
        explanation_match = re.search(r"EXPLANATION:\s*(.+)", text, re.IGNORECASE | re.DOTALL)

        if verdict_match:
            verdict = verdict_match.group(1).upper() == "PASS"
        else:
            if "PASS" in text.upper() and "FAIL" not in text.upper():
                verdict = True
            elif "FAIL" in text.upper():
                verdict = False
            else:
                verdict = False

        if explanation_match:
            explanation = explanation_match.group(1).strip()
        else:
            explanation = text.strip()[:200]

        return verdict, explanation


class DummyJudgeAdapter(JudgeAdapter):
    """
    Dummy judge adapter for testing.

    Always returns a configurable verdict.
    """

    def __init__(self, default_verdict: bool = True):
        """
        Initialize dummy judge.

        Args:
            default_verdict: Default verdict to return
        """
        self.default_verdict = default_verdict

    def judge(self, prompt: str, budget: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Return dummy judgment.

        Args:
            prompt: Judge prompt (ignored)
            budget: Budget (ignored)

        Returns:
            Dummy judgment result
        """
        return {
            "verdict": self.default_verdict,
            "explanation": "Dummy judge response",
            "tokens_used": 100,
            "latency_ms": 50.0,
            "raw_response": "VERDICT: PASS\nEXPLANATION: Dummy judge",
        }


def create_judge_adapter(
    adapter_type: str = "openai", model: str = "gpt-3.5-turbo", **kwargs: Any
) -> JudgeAdapter:
    """
    Create a judge adapter.

    Args:
        adapter_type: Type of adapter ("openai" or "dummy")
        model: Model name
        **kwargs: Additional arguments

    Returns:
        Configured JudgeAdapter
    """
    if adapter_type == "openai":
        api_key = kwargs.get("api_key")
        return OpenAIJudgeAdapter(model, api_key)
    elif adapter_type == "dummy":
        default_verdict = kwargs.get("default_verdict", True)
        return DummyJudgeAdapter(default_verdict)
    else:
        raise ValueError(f"Unknown judge adapter type: {adapter_type}")
