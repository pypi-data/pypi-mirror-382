"""
Load and validate PCSL artefacts (PD, ES, EP) from JSON or YAML files.
"""

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from promptcontracts.utils.errors import SpecValidationError


def load_json_or_yaml(path: str) -> dict[str, Any]:
    """Load a file as JSON or YAML and return a dict."""
    path_obj = Path(path)

    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path}")

    content = path_obj.read_text()

    # Try JSON first
    if path_obj.suffix.lower() == ".json":
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}") from e

    # Try YAML
    if path_obj.suffix.lower() in [".yaml", ".yml"]:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}") from e

    # Auto-detect: try JSON first, then YAML
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"File is neither valid JSON nor YAML: {e}") from e


def _get_schema_path(schema_name: str) -> Path:
    """Get the path to a PCSL schema file."""
    # Get the package root
    package_root = Path(__file__).parent.parent
    schema_dir = package_root / "spec" / "schema"
    return schema_dir / schema_name


def _validate_against_schema(
    data: dict[str, Any], schema_name: str, artefact_type: str, path: str = ""
):
    """Validate data against a PCSL schema."""
    schema_path = _get_schema_path(schema_name)

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    schema = json.loads(schema_path.read_text())

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        error_msg = f"{e.message}\nPath: {'.'.join(str(p) for p in e.path)}"
        raise SpecValidationError(artefact_type, path, error_msg) from e
    except jsonschema.SchemaError as e:
        raise SpecValidationError(artefact_type, path, f"Schema error in {schema_name}: {e}") from e


def load_pd(path: str) -> dict[str, Any]:
    """Load and validate a Prompt Definition (PD)."""
    data = load_json_or_yaml(path)
    _validate_against_schema(data, "pcsl-pd.schema.json", "Prompt Definition", path)
    return data


def load_es(path: str) -> dict[str, Any]:
    """Load and validate an Expectation Suite (ES)."""
    data = load_json_or_yaml(path)
    _validate_against_schema(data, "pcsl-es.schema.json", "Expectation Suite", path)
    return data


def load_ep(path: str) -> dict[str, Any]:
    """Load and validate an Evaluation Profile (EP)."""
    data = load_json_or_yaml(path)
    _validate_against_schema(data, "pcsl-ep.schema.json", "Evaluation Profile", path)

    # Apply default values for execution config
    if "execution" not in data:
        data["execution"] = {}

    execution = data["execution"]
    execution.setdefault("mode", "auto")
    execution.setdefault("max_retries", 1)
    execution.setdefault("strict_enforce", False)

    if "auto_repair" not in execution:
        execution["auto_repair"] = {}

    auto_repair = execution["auto_repair"]
    auto_repair.setdefault("strip_markdown_fences", True)
    auto_repair.setdefault("lowercase_fields", [])

    return data
