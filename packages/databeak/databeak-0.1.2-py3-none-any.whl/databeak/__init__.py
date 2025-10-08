"""DataBeak - MCP server for comprehensive CSV operations."""

__author__ = "Jonathan Springer"

from ._version import __version__
from .server import main, mcp

__all__ = ["__version__", "main", "mcp"]
