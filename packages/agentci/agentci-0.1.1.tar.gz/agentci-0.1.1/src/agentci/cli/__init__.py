import argparse
import sys
from pathlib import Path
from importlib.metadata import version

from agentci.client_config import discover_evaluations

__version__ = version("agentci")



def validate_command(args):
    """Validate AgentCI configuration files in the current directory."""
    # Use the provided path or current working directory
    repo_path = Path(args.path) if args.path else Path.cwd()

    if not repo_path.exists():
        print(f"Error: Directory '{repo_path}' does not exist.", file=sys.stderr)
        return 1

    if not repo_path.is_dir():
        print(f"Error: '{repo_path}' is not a directory.", file=sys.stderr)
        return 1

    print(f"Validating AgentCI configurations in: {repo_path}")

    try:
        evaluations = discover_evaluations(repo_path)

        if not evaluations:
            print("\nNo evaluation configurations found.")
            print(f"Place your .toml files in: {repo_path}/.agentci/evals/")
            return 0

        print(f"\n✓ Found {len(evaluations)} valid evaluation configuration(s):")
        for eval_config in evaluations:
            print(f" - {eval_config.name} ({eval_config.type.value}): {eval_config.description}")
            print(f"    File: {eval_config.file_path}")
            print(f"    Targets: {len(eval_config.targets.agents)} agent(s), {len(eval_config.targets.tools)} tool(s)")
            print(f"    Cases: {len(eval_config.cases)}")

        print(f"\n✓ All configurations are valid!")
        return 0

    except ValueError as e:
        print(f"\n✗ Validation failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description=f"Agent CI CLI v{__version__}",
        prog="agentci",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate AgentCI configuration files",
        description="Discover and validate AgentCI evaluation configuration files in a directory",
    )
    validate_parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to the repository (defaults to current directory)",
    )

    args = parser.parse_args()

    if args.command == "validate":
        return validate_command(args)
    else:
        # No command specified, show help
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
