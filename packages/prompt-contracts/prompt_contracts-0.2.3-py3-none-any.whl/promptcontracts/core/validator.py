"""
Validator: Check registry and execution.
"""

import json
import re
from collections.abc import Callable
from typing import Any

from jsonpath_ng import parse as jsonpath_parse

from .checks import (
    enum_check,
    json_required_check,
    json_valid_check,
    latency_budget_check,
    regex_absent_check,
    token_budget_check,
)


class CheckRegistry:
    """Registry for check types."""

    def __init__(self):
        self._checks: dict[str, Callable] = {}
        self._register_builtin_checks()

    def _register_builtin_checks(self):
        """Register all built-in check types."""
        self.register("pc.check.json_valid", json_valid_check)
        self.register("pc.check.json_required", json_required_check)
        self.register("pc.check.enum", enum_check)
        self.register("pc.check.regex_absent", regex_absent_check)
        self.register("pc.check.token_budget", token_budget_check)
        self.register("pc.check.latency_budget", latency_budget_check)

    def register(self, check_type: str, check_func: Callable):
        """Register a check function."""
        self._checks[check_type] = check_func

    def get(self, check_type: str) -> Callable:
        """Get a check function by type."""
        if check_type not in self._checks:
            raise ValueError(f"Unknown check type: {check_type}")
        return self._checks[check_type]

    def has(self, check_type: str) -> bool:
        """Check if a check type is registered."""
        return check_type in self._checks


class Validator:
    """Execute checks against responses."""

    def __init__(self, registry: CheckRegistry = None):
        self.registry = registry or CheckRegistry()

    def run_check(
        self,
        check_spec: dict[str, Any],
        response_text: str,
        parsed_json: Any = None,
        all_latencies: list[int] = None,
    ) -> dict[str, Any]:
        """
        Run a single check.

        Returns:
            {
                'type': str,
                'passed': bool,
                'message': str,
                'data': Any (optional additional data)
            }
        """
        check_type = check_spec.get("type", "")

        if not self.registry.has(check_type):
            return {
                "type": check_type,
                "passed": False,
                "message": f"Unknown check type: {check_type}",
                "data": None,
            }

        check_func = self.registry.get(check_type)

        try:
            passed, message, data = check_func(
                response_text=response_text,
                check_spec=check_spec,
                parsed_json=parsed_json,
                all_latencies=all_latencies,
            )

            return {"type": check_type, "passed": passed, "message": message, "data": data}
        except Exception as e:
            return {
                "type": check_type,
                "passed": False,
                "message": f"Check execution failed: {e}",
                "data": None,
            }

    def run_checks(
        self,
        check_specs: list[dict[str, Any]],
        response_text: str,
        parsed_json: Any = None,
        all_latencies: list[int] = None,
    ) -> list[dict[str, Any]]:
        """Run all checks and return results."""
        results = []

        for check_spec in check_specs:
            result = self.run_check(
                check_spec=check_spec,
                response_text=response_text,
                parsed_json=parsed_json,
                all_latencies=all_latencies,
            )
            results.append(result)

        return results


def normalize_output(raw_text: str, auto_repair_cfg: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """
    Normalize output based on auto-repair configuration.

    Args:
        raw_text: Raw response text
        auto_repair_cfg: Auto-repair configuration with:
            - lowercase_fields: list of JSONPath fields to lowercase
            - strip_markdown_fences: bool to strip ``` fences

    Returns:
        (normalized_text, details_dict)
    """
    normalized = raw_text
    details = {"stripped_fences": False, "lowercased_fields": []}

    # Strip markdown fences
    if auto_repair_cfg.get("strip_markdown_fences", True):
        # Remove ```json or ``` at start/end
        original = normalized
        normalized = re.sub(r"^```(?:json)?\s*\n?", "", normalized, flags=re.MULTILINE)
        normalized = re.sub(r"\n?```\s*$", "", normalized, flags=re.MULTILINE)
        normalized = normalized.strip()

        if normalized != original:
            details["stripped_fences"] = True

    # Lowercase specified JSONPath fields
    lowercase_fields = auto_repair_cfg.get("lowercase_fields", [])
    if lowercase_fields:
        try:
            parsed = json.loads(normalized)

            for field_path in lowercase_fields:
                try:
                    jsonpath_expr = jsonpath_parse(field_path)
                    matches = jsonpath_expr.find(parsed)

                    for match in matches:
                        if isinstance(match.value, str):
                            # Update the value in place
                            match.full_path.update(parsed, match.value.lower())
                            details["lowercased_fields"].append(field_path)
                except Exception:
                    # Skip invalid JSONPath or non-string values
                    continue

            # Re-serialize to JSON
            normalized = json.dumps(parsed, separators=(",", ":"))
        except json.JSONDecodeError:
            # Can't parse as JSON, skip field lowercasing
            pass

    return normalized, details


def derive_json_schema_from_es(es: dict[str, Any]) -> dict[str, Any]:
    """
    Derive a minimal JSON schema from an Expectation Suite.

    Currently supports:
    - required fields from pc.check.json_required
    - enum constraints from pc.check.enum (top-level properties only)

    Args:
        es: Expectation Suite dict

    Returns:
        JSON Schema dict
    """
    schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": True}

    checks = es.get("checks", [])

    for check in checks:
        check_type = check.get("type", "")

        # Extract required fields
        if check_type == "pc.check.json_required":
            required_fields = check.get("fields", [])
            schema["required"].extend(required_fields)

            # Add properties with default string type
            for field in required_fields:
                if field not in schema["properties"]:
                    schema["properties"][field] = {"type": "string"}

        # Extract enum constraints (top-level only for MVP)
        if check_type == "pc.check.enum":
            field_path = check.get("field", "")
            allowed_values = check.get("allowed", [])

            # Only handle simple top-level fields like "$.priority"
            if field_path.startswith("$.") and "." not in field_path[2:]:
                field_name = field_path[2:]  # Remove "$."

                schema["properties"][field_name] = {"type": "string", "enum": allowed_values}

    # Remove duplicates from required
    schema["required"] = list(set(schema["required"]))

    # Add $schema for completeness
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"

    return schema


def build_constraints_block(es: dict[str, Any]) -> str:
    """
    Build a constraints block from ES checks for prompt augmentation.

    Args:
        es: Expectation Suite dict

    Returns:
        Constraints text block
    """
    constraints = []
    checks = es.get("checks", [])

    # Process checks in deterministic order
    check_order = [
        "pc.check.json_valid",
        "pc.check.json_required",
        "pc.check.enum",
        "pc.check.regex_absent",
        "pc.check.token_budget",
        "pc.check.latency_budget",
    ]

    for check_type in check_order:
        matching_checks = [c for c in checks if c.get("type") == check_type]

        for check in matching_checks:
            if check_type == "pc.check.json_valid":
                constraints.append("- Output MUST be strict JSON.")

            elif check_type == "pc.check.json_required":
                fields = check.get("fields", [])
                if fields:
                    constraints.append(f"- Required fields: {', '.join(fields)}.")

            elif check_type == "pc.check.enum":
                field_path = check.get("field", "")
                allowed = check.get("allowed", [])
                case_insensitive = check.get("case_insensitive", False)

                # Extract field name from JSONPath
                field_name = (
                    field_path.replace("$.", "") if field_path.startswith("$.") else field_path
                )

                casing_note = (
                    " (lowercase)"
                    if not case_insensitive
                    and all(v.islower() for v in allowed if isinstance(v, str))
                    else ""
                )
                constraints.append(
                    f"- `{field_name}` MUST be exactly one of: {', '.join(map(str, allowed))}{casing_note}."
                )

            elif check_type == "pc.check.regex_absent":
                pattern = check.get("pattern", "")
                if pattern == "```":
                    constraints.append("- Do NOT include markdown code fences (```).")
                else:
                    constraints.append(f"- Do NOT include pattern: {pattern}")

            elif check_type == "pc.check.token_budget":
                max_out = check.get("max_out", 0)
                if max_out:
                    constraints.append(f"- Keep response under {max_out} tokens/words.")

    if not constraints:
        return ""

    return "\n\n[CONSTRAINTS]\n" + "\n".join(constraints)
