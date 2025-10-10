"""CLI interface for prompt-contracts."""

import argparse
import sys

from . import __version__
from .core.loader import load_ep, load_es, load_pd
from .core.reporters import CLIReporter, JSONReporter, JUnitReporter
from .core.runner import ContractRunner


def validate_command(args):
    """
    Validate a PCSL artefact against its schema.

    Exit codes:
        0: Validation successful
        2: Validation failed (schema error)
    """
    artefact_type = args.type
    path = args.path

    try:
        if artefact_type == "pd":
            data = load_pd(path)
            print(f"✓ Valid Prompt Definition: {path}")
        elif artefact_type == "es":
            data = load_es(path)
            print(f"✓ Valid Expectation Suite: {path}")
        elif artefact_type == "ep":
            data = load_ep(path)
            print(f"✓ Valid Evaluation Profile: {path}")
        else:
            print(f"✗ Unknown artefact type: {artefact_type}")
            return 2

        print(f"  PCSL version: {data.get('pcsl')}")
        if "id" in data:
            print(f"  ID: {data.get('id')}")

        return 0
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 2


def run_command(args):
    """
    Run a complete contract.

    Exit codes:
        0: All fixtures passed or were repaired successfully
        1: One or more fixtures failed or marked NONENFORCEABLE
        2: PD/ES/EP validation error
        3: Runtime/adapter error
    """
    try:
        # Load artefacts
        if args.verbose:
            print("Loading artefacts...")
        pd = load_pd(args.pd)
        es = load_es(args.es)
        ep = load_ep(args.ep)

        if args.verbose:
            print(f"✓ Loaded PD: {args.pd}")
            print(f"✓ Loaded ES: {args.es}")
            print(f"✓ Loaded EP: {args.ep}")

        if args.save_io and args.verbose:
            print(f"✓ Artifacts will be saved to: {args.save_io}")
            print()

    except Exception as e:
        print(f"✗ Validation error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 2

    try:
        # Run contract
        runner = ContractRunner(pd, es, ep, save_io_dir=args.save_io)
        results = runner.run()

        # Report results
        report_type = args.report or "cli"
        output_path = args.out

        if report_type == "cli":
            reporter = CLIReporter()
        elif report_type == "json":
            reporter = JSONReporter()
        elif report_type == "junit":
            reporter = JUnitReporter()
        else:
            print(f"Unknown report type: {report_type}")
            return 3

        reporter.report(results, output_path)

        # Determine exit code based on results
        # 0 = all PASS or REPAIRED
        # 1 = any FAIL or NONENFORCEABLE
        any_failed = any(
            t.get("summary", {}).get("status") == "RED" for t in results.get("targets", [])
        )

        return 1 if any_failed else 0

    except Exception as e:
        print(f"✗ Runtime error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 3


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="prompt-contracts",
        description="Test your LLM prompts like code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate artefacts
  prompt-contracts validate pd examples/support_ticket/pd.json
  prompt-contracts validate es examples/support_ticket/es.json
  prompt-contracts validate ep examples/support_ticket/ep.json

  # Run contract with CLI report
  prompt-contracts run \\
    --pd examples/support_ticket/pd.json \\
    --es examples/support_ticket/es.json \\
    --ep examples/support_ticket/ep.json \\
    --report cli

  # Run with artifacts saved
  prompt-contracts run \\
    --pd examples/support_ticket/pd.json \\
    --es examples/support_ticket/es.json \\
    --ep examples/support_ticket/ep.json \\
    --save-io artifacts/ \\
    --report json --out results.json

Exit codes:
  0  All fixtures passed or repaired successfully
  1  One or more fixtures failed or marked NONENFORCEABLE
  2  PD/ES/EP validation error
  3  Runtime/adapter error
""",
    )

    parser.add_argument("--version", action="version", version=f"prompt-contracts {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a PCSL artefact",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    validate_parser.add_argument(
        "type", choices=["pd", "es", "ep"], help="Artefact type (pd, es, or ep)"
    )
    validate_parser.add_argument("path", help="Path to artefact file")
    validate_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Run command
    run_parser = subparsers.add_parser(
        "run",
        help="Run a contract",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    run_parser.add_argument("--pd", required=True, help="Path to Prompt Definition (JSON/YAML)")
    run_parser.add_argument("--es", required=True, help="Path to Expectation Suite (JSON/YAML)")
    run_parser.add_argument("--ep", required=True, help="Path to Evaluation Profile (JSON/YAML)")
    run_parser.add_argument(
        "--report",
        choices=["cli", "json", "junit"],
        default="cli",
        help="Report format (default: cli)",
    )
    run_parser.add_argument("--out", help="Output path for report file (optional)")
    run_parser.add_argument(
        "--save-io",
        dest="save_io",
        help="Directory to save execution artifacts (input_final.txt, output_raw.txt, output_norm.txt, run.json)",
    )
    run_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.command == "validate":
        sys.exit(validate_command(args))
    elif args.command == "run":
        sys.exit(run_command(args))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
