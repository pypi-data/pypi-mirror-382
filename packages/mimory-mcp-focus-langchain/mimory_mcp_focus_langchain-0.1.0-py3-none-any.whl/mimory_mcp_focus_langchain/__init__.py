"""mim-mcp-focus-langchain: LangChain integration for mim-mcp-focus.

This package provides easy integration between mim-mcp-focus and LangChain,
allowing you to add focus capabilities to your LangChain MCP implementations.
"""

from .client import FocusMultiServerMCPClient

__all__ = [
    "FocusMultiServerMCPClient"
]
