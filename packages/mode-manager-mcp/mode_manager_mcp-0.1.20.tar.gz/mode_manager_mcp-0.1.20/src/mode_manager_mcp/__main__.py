#!/usr/bin/env python3
"""
Main entry point for the Mode Manager MCP Server.

This script provides the command-line interface to run the MCP server
for managing VS Code .chatmode.md and .instructions.md files (GitHub Copilot prompts).
"""

import argparse
import logging
import sys

from .simple_server import create_server


def setup_logging(debug: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    import os
    import tempfile

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    try:
        temp_log_dir = os.path.join(tempfile.gettempdir(), "mode_manager_logs")
        os.makedirs(temp_log_dir, exist_ok=True)
        log_path = os.path.join(temp_log_dir, "mode_manager.log")
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        handlers.append(file_handler)
        print(f"[Mode Manager MCP] Log file: {log_path}", file=sys.stderr)
    except Exception:
        pass  # If file can't be opened, just use stderr

    handlers[0].setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Mode Manager MCP Server - Manage .chatmode.md files for GitHub Copilot",
        prog="mode-manager-mcp",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Run server in read-only mode (no write operations)",
    )

    parser.add_argument(
        "--library-url",
        type=str,
        help="Custom URL for the Mode Manager MCP Library (defaults to official GitHub repo). Can also be set via MCP_LIBRARY_URL environment variable.",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.2.0")

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_arguments()

    # Set up logging
    setup_logging(args.debug)

    # Set read-only mode environment variable if specified
    if args.read_only:
        import os

        os.environ["MCP_CHATMODE_READ_ONLY"] = "true"

    # Create and run the server
    from . import __version__

    logging.info(f"Running version {__version__}")
    server = create_server(library_url=args.library_url)

    try:
        # Run the server with stdio transport (MCP standard)
        server.run()

    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
