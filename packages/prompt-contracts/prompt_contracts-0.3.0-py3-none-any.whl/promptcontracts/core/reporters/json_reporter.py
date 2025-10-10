"""JSON reporter for machine-readable output."""

import json
from pathlib import Path
from typing import Any


class JSONReporter:
    """JSON reporter."""

    def report(self, results: dict[str, Any], output_path: str = None):
        """
        Write results as JSON (includes artifact paths).

        Args:
            results: Results from ContractRunner
            output_path: Path to write JSON (if None, print to stdout)
        """
        # Enrich results with metadata (v0.3.0)
        enriched = {
            **results,
            "_metadata": {
                "pcsl_version": results.get("pcsl_version", "0.3.0"),
                "artifact_base_dir": results.get("artifact_base_dir"),
                "timestamp": (
                    results.get("targets", [{}])[0]
                    .get("fixtures", [{}])[0]
                    .get("artifact_paths", {})
                    .get("run")
                    if results.get("targets")
                    else None
                ),
                "sampling_enabled": any(
                    t.get("execution", {}).get("sampling", {}).get("n", 1) > 1
                    for t in results.get("targets", [])
                ),
            },
        }

        json_output = json.dumps(enriched, indent=2)

        if output_path:
            Path(output_path).write_text(json_output)
            print(f"Results written to {output_path}")
            if results.get("artifact_base_dir"):
                print(f"Artifacts saved to {results['artifact_base_dir']}")
        else:
            print(json_output)
