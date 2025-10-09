"""
Main runner: orchestrate contract execution with enforcement and retries.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .adapters import OllamaAdapter, OpenAIAdapter
from .validator import (
    CheckRegistry,
    Validator,
    build_constraints_block,
    derive_json_schema_from_es,
    normalize_output,
)


class ContractRunner:
    """Execute PCSL contracts with enforcement modes."""

    def __init__(
        self,
        pd: dict[str, Any],
        es: dict[str, Any],
        ep: dict[str, Any],
        save_io_dir: str | None = None,
    ):
        """
        Initialize runner with artefacts.

        Args:
            pd: Prompt Definition
            es: Expectation Suite
            ep: Evaluation Profile
            save_io_dir: Optional directory to save IO artifacts
        """
        self.pd = pd
        self.es = es
        self.ep = ep
        self.save_io_dir = Path(save_io_dir) if save_io_dir else None
        self.validator = Validator(CheckRegistry())

        # Parse execution config with defaults
        execution = ep.get("execution", {})
        self.exec_mode = execution.get("mode", "auto")
        self.max_retries = execution.get("max_retries", 1)
        self.strict_enforce = execution.get("strict_enforce", False)
        self.auto_repair_cfg = execution.get(
            "auto_repair", {"strip_markdown_fences": True, "lowercase_fields": []}
        )

    def _create_adapter(self, target: dict[str, Any]):
        """Create an adapter for a target."""
        target_type = target.get("type")
        model = target.get("model")
        params = target.get("params", {})

        if target_type == "openai":
            return OpenAIAdapter(model, params)
        elif target_type == "ollama":
            return OllamaAdapter(model, params)
        else:
            raise ValueError(f"Unknown target type: {target_type}")

    def _determine_effective_mode(
        self, requested_mode: str, adapter_capabilities
    ) -> tuple[str, bool]:
        """
        Determine effective execution mode based on capabilities.

        Returns:
            (effective_mode, is_nonenforceable)
        """
        if requested_mode == "observe":
            return "observe", False

        if requested_mode == "assist":
            return "assist", False

        if requested_mode == "enforce":
            if adapter_capabilities.schema_guided_json:
                return "enforce", False
            else:
                # If strict_enforce is True, mark as NONENFORCEABLE
                # Otherwise fallback to assist
                if self.strict_enforce:
                    return "enforce", True  # NONENFORCEABLE
                else:
                    return "assist", False  # Fallback to assist

        if requested_mode == "auto":
            if adapter_capabilities.schema_guided_json:
                return "enforce", False
            else:
                return "assist", False

        return "observe", False

    def _build_prompt(self, fixture: dict[str, Any], effective_mode: str) -> str:
        """Build final prompt with fixture input and optional constraints."""
        base_prompt = self.pd.get("prompt", "")
        fixture_input = fixture.get("input", "")

        # Combine base + fixture input
        prompt = f"{base_prompt}\n\n[USER INPUT]\n{fixture_input}"

        # Add constraints block for assist/enforce modes
        if effective_mode in ["assist", "enforce"]:
            constraints = build_constraints_block(self.es)
            if constraints:
                prompt += constraints

        return prompt

    def _save_artifacts(
        self,
        target_id: str,
        fixture_id: str,
        final_prompt: str,
        raw_output: str,
        normalized_output: str,
        metadata: dict[str, Any],
    ):
        """Save IO artifacts to disk."""
        if not self.save_io_dir:
            return

        artifact_dir = self.save_io_dir / target_id / fixture_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        (artifact_dir / "input_final.txt").write_text(final_prompt)
        (artifact_dir / "output_raw.txt").write_text(raw_output)
        (artifact_dir / "output_norm.txt").write_text(normalized_output)
        (artifact_dir / "run.json").write_text(json.dumps(metadata, indent=2))

        return str(artifact_dir)

    def _validate_response(
        self, response_text: str, parsed_json: Any = None
    ) -> list[dict[str, Any]]:
        """Run validation checks on response."""
        checks = self.es.get("checks", [])

        # Filter out latency checks (handled separately)
        non_latency_checks = [c for c in checks if c.get("type") != "pc.check.latency_budget"]

        return self.validator.run_checks(
            check_specs=non_latency_checks, response_text=response_text, parsed_json=parsed_json
        )

    def _run_fixture_with_retry(
        self, adapter, schema: dict | None, final_prompt: str, fixture_id: str
    ) -> dict[str, Any]:
        """
        Run a fixture with retry and auto-repair logic.

        Returns fixture result dict with status, checks, retries_used, etc.
        """
        retries_used = 0
        raw_output = ""
        normalized_output = ""
        repair_details = {}
        status = "FAIL"
        all_check_results = []
        total_latency = 0

        for attempt in range(self.max_retries + 1):
            # Generate response
            raw_output, latency_ms = adapter.generate(final_prompt, schema=schema)
            total_latency += latency_ms

            # Start with raw output
            normalized_output = raw_output
            repair_details = {"stripped_fences": False, "lowercased_fields": []}

            # Parse JSON if expected
            parsed_json = None
            if self.pd.get("io", {}).get("expects") == "structured/json":
                try:
                    parsed_json = json.loads(normalized_output)
                except json.JSONDecodeError:
                    pass

            # Validate
            check_results = self._validate_response(normalized_output, parsed_json)
            all_passed = all(r["passed"] for r in check_results)

            if all_passed:
                status = "PASS" if attempt == 0 else "REPAIRED"
                all_check_results = check_results
                break

            # If not passed and retries remain, try auto-repair
            if attempt < self.max_retries:
                retries_used += 1

                # Apply auto-repair
                normalized_output, repair_details = normalize_output(
                    raw_output, self.auto_repair_cfg
                )

                # Re-parse after normalization
                if self.pd.get("io", {}).get("expects") == "structured/json":
                    try:
                        parsed_json = json.loads(normalized_output)
                    except json.JSONDecodeError:
                        parsed_json = None

                # Re-validate
                check_results = self._validate_response(normalized_output, parsed_json)
                all_passed = all(r["passed"] for r in check_results)

                if all_passed:
                    status = "REPAIRED"
                    all_check_results = check_results
                    break
            else:
                # Out of retries
                all_check_results = check_results
                status = "FAIL"

        return {
            "fixture_id": fixture_id,
            "raw_output": raw_output,
            "normalized_output": normalized_output,
            "latency_ms": total_latency,
            "retries_used": retries_used,
            "repair_details": repair_details,
            "status": status,
            "checks": all_check_results,
        }

    def run(self) -> dict[str, Any]:
        """
        Execute the contract and return results.

        Returns:
            Results dict with targets, fixtures, summaries, and artifact paths
        """
        targets = self.ep.get("targets", [])
        fixtures = self.ep.get("fixtures", [])
        checks = self.es.get("checks", [])

        results = {
            "targets": [],
            "artifact_base_dir": str(self.save_io_dir) if self.save_io_dir else None,
        }

        for target in targets:
            adapter = self._create_adapter(target)
            capabilities = adapter.capabilities()

            # Determine effective mode
            effective_mode, is_nonenforceable = self._determine_effective_mode(
                self.exec_mode, capabilities
            )

            target_id = f"{target.get('type')}:{target.get('model')}"

            # Derive schema if enforce mode
            schema = None
            if effective_mode == "enforce" and capabilities.schema_guided_json:
                schema = derive_json_schema_from_es(self.es)

            target_result = {
                "target": target,
                "target_id": target_id,
                "execution": {
                    "requested_mode": self.exec_mode,
                    "effective_mode": effective_mode,
                    "is_nonenforceable": is_nonenforceable,
                    "max_retries": self.max_retries,
                },
                "fixtures": [],
                "summary": {},
            }

            all_latencies = []
            all_check_results = []

            # Run each fixture
            for fixture in fixtures:
                fixture_id = fixture.get("id")
                final_prompt = self._build_prompt(fixture, effective_mode)

                # Run with retry logic
                fixture_result = self._run_fixture_with_retry(
                    adapter, schema, final_prompt, fixture_id
                )

                all_latencies.append(fixture_result["latency_ms"])
                all_check_results.extend(fixture_result["checks"])

                # Save artifacts
                artifact_path = None
                if self.save_io_dir:
                    # Compute prompt hash
                    prompt_hash = hashlib.sha256(final_prompt.encode()).hexdigest()

                    metadata = {
                        "pcsl": self.pd.get("pcsl", "0.1.0"),
                        "target": target_id,
                        "params": target.get("params", {}),
                        "execution": {
                            "mode": self.exec_mode,
                            "effective_mode": effective_mode,
                            "max_retries": self.max_retries,
                        },
                        "latency_ms": fixture_result["latency_ms"],
                        "retries_used": fixture_result["retries_used"],
                        "status": fixture_result["status"],
                        "repaired_details": fixture_result["repair_details"],
                        "checks": fixture_result["checks"],
                        "prompt_hash": prompt_hash,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }

                    artifact_path = self._save_artifacts(
                        target_id,
                        fixture_id,
                        final_prompt,
                        fixture_result["raw_output"],
                        fixture_result["normalized_output"],
                        metadata,
                    )

                # Add to results
                target_result["fixtures"].append(
                    {
                        "fixture_id": fixture_id,
                        "status": fixture_result["status"],
                        "latency_ms": fixture_result["latency_ms"],
                        "retries_used": fixture_result["retries_used"],
                        "repaired_details": fixture_result["repair_details"],
                        "checks": fixture_result["checks"],
                        "artifact_path": artifact_path,
                    }
                )

            # Run latency budget checks if any
            latency_checks = [c for c in checks if c.get("type") == "pc.check.latency_budget"]
            for check in latency_checks:
                result = self.validator.run_check(
                    check_spec=check,
                    response_text="",
                    all_latencies=all_latencies,
                )
                all_check_results.append(result)

            # Calculate summary
            total_checks = len(all_check_results)
            passed_checks = sum(1 for r in all_check_results if r["passed"])
            pass_rate = passed_checks / total_checks if total_checks > 0 else 0

            # Count statuses
            fixture_statuses = [f["status"] for f in target_result["fixtures"]]
            status_counts = {
                "PASS": fixture_statuses.count("PASS"),
                "REPAIRED": fixture_statuses.count("REPAIRED"),
                "FAIL": fixture_statuses.count("FAIL"),
                "NONENFORCEABLE": 1 if is_nonenforceable else 0,
            }

            # Determine overall status
            if is_nonenforceable:
                status = "YELLOW"
            elif status_counts["FAIL"] > 0:
                status = "RED"
            elif status_counts["REPAIRED"] > 0:
                status = "YELLOW"
            else:
                status = "GREEN"

            target_result["summary"] = {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "pass_rate": pass_rate,
                "status": status,
                "fixture_statuses": status_counts,
            }

            results["targets"].append(target_result)

        return results
