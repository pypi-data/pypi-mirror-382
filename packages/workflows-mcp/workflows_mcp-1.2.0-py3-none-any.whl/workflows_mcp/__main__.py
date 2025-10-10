"""Entry point for workflows-mcp MCP server.

This module provides the main entry point for running the MCP server
via `uv run` or direct execution. Follows the official Anthropic MCP
Python SDK patterns.
"""


def main() -> None:
    """Entry point for direct execution."""
    from .server import mcp

    mcp.run()


if __name__ == "__main__":
    main()
