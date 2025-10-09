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
        # Enrich results with metadata
        enriched = {
            **results,
            "_metadata": {
                "artifact_base_dir": results.get("artifact_base_dir"),
                "timestamp": (
                    results.get("targets", [{}])[0].get("fixtures", [{}])[0].get("timestamp")
                    if results.get("targets")
                    else None
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
