"""
Main runner: orchestrate contract execution with enforcement, sampling, and retries.

Version 0.3.0: Added probabilistic sampling, enhanced parsing, repair policies,
and capability negotiation.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .adapters import OllamaAdapter, OpenAIAdapter
from .capability import CapabilityNegotiator, ProviderCapabilities
from .parser import json_loose
from .sampling import SampleResult, create_sampler
from .validator import CheckRegistry, Validator, build_constraints_block, derive_json_schema_from_es


class ContractRunner:
    """Execute PCSL contracts with enforcement modes, sampling, and repair."""

    def __init__(
        self,
        pd: dict[str, Any],
        es: dict[str, Any],
        ep: dict[str, Any],
        save_io_dir: str | None = None,
        embedding_adapter: Any = None,
        judge_adapter: Any = None,
    ):
        """
        Initialize runner with artifacts.

        Args:
            pd: Prompt Definition
            es: Expectation Suite
            ep: Evaluation Profile
            save_io_dir: Optional directory to save IO artifacts
            embedding_adapter: Optional embedding adapter for similarity checks
            judge_adapter: Optional judge adapter for LLM-as-judge checks
        """
        self.pd = pd
        self.es = es
        self.ep = ep
        self.save_io_dir = Path(save_io_dir) if save_io_dir else None
        self.validator = Validator(CheckRegistry())
        self.embedding_adapter = embedding_adapter
        self.judge_adapter = judge_adapter

        # Parse execution config with defaults
        execution = ep.get("execution", {})
        self.exec_mode = execution.get("mode", "auto")
        self.max_retries = execution.get("max_retries", 1)
        self.strict_enforce = execution.get("strict_enforce", False)
        self.auto_repair_cfg = execution.get(
            "auto_repair", {"strip_markdown_fences": True, "lowercase_fields": []}
        )

        # v0.3.0: Repair policy
        self.repair_policy = execution.get(
            "repair_policy",
            {
                "enabled": True,
                "max_steps": 1,
                "allowed": ["strip_markdown_fences", "json_loose_parse"],
            },
        )

        # v0.3.0: Sampling config
        sampling_cfg = ep.get("sampling", {})
        self.n_samples = sampling_cfg.get("n", 1)
        self.seed = sampling_cfg.get("seed")
        self.aggregation = sampling_cfg.get("aggregation", "first")
        self.bootstrap_samples = sampling_cfg.get("bootstrap_samples", 1000)

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
        self, requested_mode: str, adapter
    ) -> tuple[str, bool, list[str]]:
        """
        Determine effective execution mode using capability negotiation.

        Returns:
            (effective_mode, is_nonenforceable, negotiation_log)
        """
        capabilities = adapter.capabilities()

        # Convert to ProviderCapabilities
        provider_caps = ProviderCapabilities(
            provider_type=adapter.__class__.__name__,
            model_name=adapter.model,
            schema_guided_json=capabilities.schema_guided_json,
            function_calling=capabilities.tool_calling,
            supports_seed=capabilities.supports_seed,
            supports_temperature=capabilities.supports_temperature,
            supports_top_p=capabilities.supports_top_p,
        )

        # Negotiate mode
        negotiator = CapabilityNegotiator(provider_caps, self.strict_enforce)
        result = negotiator.negotiate(requested_mode)

        return (
            result.effective_mode,
            result.is_nonenforceable,
            result.negotiation_log,
        )

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

    def _parse_output(self, raw_output: str, repair_steps: list[str]) -> tuple[str, Any, dict]:
        """
        Parse output with repair policy.

        Args:
            raw_output: Raw LLM output
            repair_steps: List of allowed repair steps

        Returns:
            (normalized_output, parsed_json, repair_details)
        """
        normalized = raw_output
        parsed = None
        repair_details = {"steps_applied": []}

        expects = self.pd.get("io", {}).get("expects", "text")

        if expects == "structured/json":
            # Try direct parse first
            try:
                parsed = json.loads(normalized)
                return normalized, parsed, repair_details
            except json.JSONDecodeError:
                pass

            # Apply repair steps
            if self.repair_policy.get("enabled", True):
                # Step 1: strip markdown fences
                if "strip_markdown_fences" in repair_steps:
                    from .parser import strip_markdown_fences

                    stripped = strip_markdown_fences(normalized)
                    if stripped != normalized:
                        normalized = stripped
                        repair_details["steps_applied"].append("strip_markdown_fences")
                        try:
                            parsed = json.loads(normalized)
                            return normalized, parsed, repair_details
                        except json.JSONDecodeError:
                            pass

                # Step 2: json_loose parse
                if "json_loose_parse" in repair_steps:
                    try:
                        parsed = json_loose(raw_output)
                        normalized = json.dumps(parsed)
                        repair_details["steps_applied"].append("json_loose_parse")
                        return normalized, parsed, repair_details
                    except Exception:
                        pass

        return normalized, parsed, repair_details

    def _validate_response(
        self, response_text: str, parsed_json: Any = None
    ) -> list[dict[str, Any]]:
        """Run validation checks on response."""
        checks = self.es.get("checks", [])

        # Filter out latency checks (handled separately)
        non_latency_checks = [c for c in checks if c.get("type") != "pc.check.latency_budget"]

        return self.validator.run_checks(
            check_specs=non_latency_checks,
            response_text=response_text,
            parsed_json=parsed_json,
            embedding_adapter=self.embedding_adapter,
            judge_adapter=self.judge_adapter,
        )

    def _run_single_sample(
        self,
        adapter,
        schema: dict | None,
        final_prompt: str,
        sample_id: int,
    ) -> SampleResult:
        """
        Run a single sample.

        Args:
            adapter: LLM adapter
            schema: Optional JSON schema
            final_prompt: Complete prompt
            sample_id: Sample identifier

        Returns:
            SampleResult with output and check results
        """
        # Generate response
        raw_output, latency_ms = adapter.generate(final_prompt, schema=schema)

        # Parse and repair
        repair_steps = self.repair_policy.get(
            "allowed", ["strip_markdown_fences", "json_loose_parse"]
        )
        normalized_output, parsed_json, repair_details = self._parse_output(
            raw_output, repair_steps
        )

        # Validate
        check_results = self._validate_response(normalized_output, parsed_json)
        checks_passed = all(r["passed"] for r in check_results)

        return SampleResult(
            sample_id=sample_id,
            output=normalized_output,
            parsed=parsed_json,
            latency_ms=latency_ms,
            checks_passed=checks_passed,
            check_results=check_results,
        )

    def _run_fixture_with_sampling(
        self,
        adapter,
        schema: dict | None,
        final_prompt: str,
        fixture_id: str,
    ) -> dict[str, Any]:
        """
        Run a fixture with N-sampling and aggregation.

        Returns fixture result dict with status, checks, sampling metadata, etc.
        """
        # Create sampler
        sampler = create_sampler(
            n=self.n_samples,
            seed=self.seed,
            aggregation=self.aggregation,
            bootstrap_samples=self.bootstrap_samples,
        )

        # Generate samples
        def generator(sample_id: int) -> SampleResult:
            return self._run_single_sample(adapter, schema, final_prompt, sample_id)

        aggregated = sampler.sample_n(generator)

        # Determine status
        if aggregated.all_passed:
            status = "PASS"
        else:
            status = "FAIL"

        # Build repair ledger from samples
        repair_ledger = []
        for sample in aggregated.samples:
            if hasattr(sample, "repair_details"):
                repair_ledger.append(sample.repair_details)

        return {
            "fixture_id": fixture_id,
            "raw_output": aggregated.samples[0].output,  # First sample raw
            "normalized_output": aggregated.selected_output,
            "latency_ms": aggregated.total_latency_ms,
            "mean_latency_ms": aggregated.mean_latency_ms,
            "retries_used": 0,  # Retries deprecated in favor of sampling
            "repair_details": {},
            "repair_ledger": repair_ledger,
            "status": status,
            "checks": (
                aggregated.selected_parsed
                if aggregated.selected_parsed
                else aggregated.samples[0].check_results
            ),
            "sampling_metadata": {
                "n_samples": len(aggregated.samples),
                "aggregation_policy": aggregated.aggregation_policy,
                "pass_rate": aggregated.pass_rate,
                "confidence_interval": aggregated.confidence_interval,
                "samples": [
                    {
                        "sample_id": s.sample_id,
                        "latency_ms": s.latency_ms,
                        "checks_passed": s.checks_passed,
                    }
                    for s in aggregated.samples
                ],
            },
        }

    def _save_artifacts(
        self,
        target_id: str,
        fixture_id: str,
        final_prompt: str,
        raw_output: str,
        normalized_output: str,
        metadata: dict[str, Any],
    ) -> dict[str, str]:
        """
        Save IO artifacts to disk.

        Returns dict with absolute paths to all artifact files.
        """
        if not self.save_io_dir:
            return {}

        artifact_dir = self.save_io_dir / target_id / fixture_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        # Save files and get absolute paths
        input_path = artifact_dir / "input_final.txt"
        output_raw_path = artifact_dir / "output_raw.txt"
        output_norm_path = artifact_dir / "output_norm.txt"
        run_json_path = artifact_dir / "run.json"

        input_path.write_text(final_prompt)
        output_raw_path.write_text(raw_output)
        output_norm_path.write_text(normalized_output)

        # Add artifact paths to metadata before saving
        artifact_paths = {
            "input_final": str(input_path.absolute()),
            "output_raw": str(output_raw_path.absolute()),
            "output_norm": str(output_norm_path.absolute()),
            "run": str(run_json_path.absolute()),
        }
        metadata["artifact_paths"] = artifact_paths

        run_json_path.write_text(json.dumps(metadata, indent=2))

        return artifact_paths

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
            "pcsl_version": "0.3.0",
        }

        for target in targets:
            adapter = self._create_adapter(target)

            # Determine effective mode using capability negotiation
            effective_mode, is_nonenforceable, negotiation_log = self._determine_effective_mode(
                self.exec_mode, adapter
            )

            target_id = f"{target.get('type')}:{target.get('model')}"

            # Derive schema if enforce mode
            schema = None
            if effective_mode == "enforce":
                capabilities = adapter.capabilities()
                if capabilities.schema_guided_json:
                    schema = derive_json_schema_from_es(self.es)

            target_result = {
                "target": target,
                "target_id": target_id,
                "execution": {
                    "requested_mode": self.exec_mode,
                    "effective_mode": effective_mode,
                    "is_nonenforceable": is_nonenforceable,
                    "negotiation_log": negotiation_log,
                    "max_retries": self.max_retries,
                    "repair_policy": self.repair_policy,
                    "sampling": {
                        "n": self.n_samples,
                        "seed": self.seed,
                        "aggregation": self.aggregation,
                    },
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

                # Run with sampling
                fixture_result = self._run_fixture_with_sampling(
                    adapter, schema, final_prompt, fixture_id
                )

                all_latencies.append(fixture_result["latency_ms"])
                all_check_results.extend(fixture_result["checks"])

                # Save artifacts and get paths
                artifact_paths = {}
                if self.save_io_dir:
                    # Compute prompt hash
                    prompt_hash = hashlib.sha256(final_prompt.encode()).hexdigest()

                    metadata = {
                        "pcsl": self.pd.get("pcsl", "0.3.0"),
                        "target": target_id,
                        "params": target.get("params", {}),
                        "execution": target_result["execution"],
                        "latency_ms": fixture_result["latency_ms"],
                        "status": fixture_result["status"],
                        "sampling_metadata": fixture_result.get("sampling_metadata", {}),
                        "repair_ledger": fixture_result.get("repair_ledger", []),
                        "checks": fixture_result["checks"],
                        "prompt_hash": prompt_hash,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }

                    artifact_paths = self._save_artifacts(
                        target_id,
                        fixture_id,
                        final_prompt,
                        fixture_result["raw_output"],
                        fixture_result["normalized_output"],
                        metadata,
                    )

                # Add to results
                fixture_result_item = {
                    "fixture_id": fixture_id,
                    "status": fixture_result["status"],
                    "latency_ms": fixture_result["latency_ms"],
                    "mean_latency_ms": fixture_result.get("mean_latency_ms", 0),
                    "sampling_metadata": fixture_result.get("sampling_metadata", {}),
                    "repair_ledger": fixture_result.get("repair_ledger", []),
                    "checks": fixture_result["checks"],
                }

                # Add artifact paths if they were saved
                if artifact_paths:
                    fixture_result_item["artifact_paths"] = artifact_paths

                target_result["fixtures"].append(fixture_result_item)

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
                "REPAIRED": 0,  # Deprecated in v0.3.0
                "FAIL": fixture_statuses.count("FAIL"),
                "NONENFORCEABLE": 1 if is_nonenforceable else 0,
            }

            # Determine overall status
            if is_nonenforceable:
                status = "YELLOW"
            elif status_counts["FAIL"] > 0:
                status = "RED"
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
