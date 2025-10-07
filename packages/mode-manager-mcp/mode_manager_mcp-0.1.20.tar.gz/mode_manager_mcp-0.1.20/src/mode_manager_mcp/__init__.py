"""
Mode Manager MCP Server.

This package provides an MCP server for managing VS Code chatmode files
and GitHub Copilot instructions. The server uses a singleton orchestration
pattern with tools organized in separate modules.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version

from .simple_server import create_server

try:
    __version__ = pkg_version("mode-manager-mcp")
except PackageNotFoundError:  # pragma: no cover - when not installed
    __version__ = "0.0.0"

__all__ = ["create_server"]
