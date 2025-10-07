"""Main CLI entry point for the EdgeAI SDK.

Provides the command-line interface by discovering and routing
to registered sub-commands through the plugin system.
"""

from __future__ import annotations

import argparse

from .commands import register_subcommands


def main() -> None:  # pragma: no cover - exercised via CLI tests
    """Main entry point for the zededa-edgeai command-line interface.
    
    Configures argument parsing with subcommands, processes user input,
    and routes execution to the appropriate command handler while providing
    consistent error handling and user feedback.
    """
    parser = argparse.ArgumentParser(
        prog="zededa-edgeai",
        description="Zededa EdgeAI CLI",
        epilog="""Environment Variables:
  EDGEAI_SERVICE_URL    EdgeAI service URL (default: https://studio.edgeai.zededa.dev)

Examples:
  %(prog)s login --catalog development
  %(prog)s login --email user@company.com --prompt-password
  EDGEAI_SERVICE_URL=https://custom.backend.com %(prog)s login --catalog test
  %(prog)s set-catalog-context production
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="command",
        title="available commands",
        metavar="COMMAND",
    )

    register_subcommands(subparsers)

    args = parser.parse_args()
    handler = getattr(args, "_command_handler", None)
    if not handler:
        parser.print_help()
        raise SystemExit(1)

    handler(args)


if __name__ == "__main__":  # pragma: no cover
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"CLI error: {exc}")
        raise SystemExit(1) from exc
