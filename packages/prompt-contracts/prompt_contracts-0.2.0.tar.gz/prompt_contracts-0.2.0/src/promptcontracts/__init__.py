"""
Prompt Contracts - Test your LLM prompts like code.

A specification and toolkit for contract testing of LLM prompts.
"""

__version__ = "0.2.0"

from .core.loader import load_ep, load_es, load_pd
from .core.runner import ContractRunner
from .utils.errors import (
    AdapterError,
    CheckFailure,
    ExecutionError,
    PromptContractsError,
    SpecValidationError,
)


def run_contract(
    pd: str, es: str, ep: str, *, report: str = "json", save_io: str = None, verbose: bool = False
) -> dict:
    """
    Run a complete prompt contract.

    Args:
        pd: Path to Prompt Definition (PD) file
        es: Path to Expectation Suite (ES) file
        ep: Path to Evaluation Profile (EP) file
        report: Report format ('cli', 'json', 'junit')
        save_io: Directory to save IO artifacts (optional)
        verbose: Enable verbose logging

    Returns:
        Dictionary containing execution results

    Raises:
        SpecValidationError: If any artifact fails validation
        ExecutionError: If contract execution fails

    Example:
        >>> results = run_contract(
        ...     pd="examples/pd.json",
        ...     es="examples/es.json",
        ...     ep="examples/ep.json",
        ...     report="json"
        ... )
        >>> print(results['status'])
        'PASS'
    """
    # Load artifacts
    pd_dict = load_pd(pd)
    es_dict = load_es(es)
    ep_dict = load_ep(ep)

    # Run contract
    runner = ContractRunner(pd_dict, es_dict, ep_dict, save_io_dir=save_io, verbose=verbose)
    results = runner.run()

    return results


def validate_artifact(kind: str, path: str) -> None:
    """
    Validate a PCSL artifact against its JSON Schema.

    Args:
        kind: Artifact type ('pd', 'es', or 'ep')
        path: Path to the artifact file

    Raises:
        SpecValidationError: If validation fails
        ValueError: If kind is not recognized

    Example:
        >>> validate_artifact('pd', 'examples/pd.json')
        # Raises SpecValidationError if invalid
    """
    kind = kind.lower()

    if kind == "pd":
        load_pd(path)
    elif kind == "es":
        load_es(path)
    elif kind == "ep":
        load_ep(path)
    else:
        raise ValueError(f"Unknown artifact kind: {kind}. Must be 'pd', 'es', or 'ep'")


__all__ = [
    "__version__",
    "run_contract",
    "validate_artifact",
    "PromptContractsError",
    "SpecValidationError",
    "AdapterError",
    "ExecutionError",
    "CheckFailure",
]
