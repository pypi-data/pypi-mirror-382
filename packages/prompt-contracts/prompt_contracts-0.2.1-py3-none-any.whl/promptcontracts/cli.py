"""CLI interface for prompt-contracts."""

import argparse
import sys

from . import __version__
from .core.loader import load_ep, load_es, load_pd
from .core.reporters import CLIReporter, JSONReporter, JUnitReporter
from .core.runner import ContractRunner


def validate_command(args):
    """Validate a PCSL artefact against its schema."""
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
            sys.exit(1)

        print(f"  PCSL version: {data.get('pcsl')}")
        if "id" in data:
            print(f"  ID: {data.get('id')}")

        return 0
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return 1


def run_command(args):
    """Run a complete contract."""
    try:
        # Load artefacts
        print("Loading artefacts...")
        pd = load_pd(args.pd)
        es = load_es(args.es)
        ep = load_ep(args.ep)

        print(f"✓ Loaded PD: {args.pd}")
        print(f"✓ Loaded ES: {args.es}")
        print(f"✓ Loaded EP: {args.ep}")

        if args.save_io:
            print(f"✓ Artifacts will be saved to: {args.save_io}")

        print()

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
            return 1

        reporter.report(results, output_path)

        # Exit with non-zero if any target failed
        any_failed = any(
            t.get("summary", {}).get("status") == "RED" for t in results.get("targets", [])
        )

        return 1 if any_failed else 0

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="prompt-contracts: Test your LLM prompts like code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--version", action="version", version=f"prompt-contracts {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a PCSL artefact")
    validate_parser.add_argument("type", choices=["pd", "es", "ep"], help="Artefact type")
    validate_parser.add_argument("path", help="Path to artefact file")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a contract")
    run_parser.add_argument("--pd", required=True, help="Path to Prompt Definition")
    run_parser.add_argument("--es", required=True, help="Path to Expectation Suite")
    run_parser.add_argument("--ep", required=True, help="Path to Evaluation Profile")
    run_parser.add_argument(
        "--report", choices=["cli", "json", "junit"], default="cli", help="Report format"
    )
    run_parser.add_argument("--out", help="Output path for report (optional)")
    run_parser.add_argument("--save-io", dest="save_io", help="Directory to save IO artifacts")

    args = parser.parse_args()

    if args.command == "validate":
        sys.exit(validate_command(args))
    elif args.command == "run":
        sys.exit(run_command(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
