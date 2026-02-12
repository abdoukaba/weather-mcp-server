#!/usr/bin/env python3
"""
Weather MCP Server Entry Point

This is the main entry point for running the Weather MCP Server.
It supports both STDIO and HTTP transports.

Usage:
    python server.py              # Run with STDIO transport (default)
    python server.py --stdio      # Explicitly use STDIO
    python server.py --http       # Run with HTTP transport
"""

from weather_mcp.server import main

if __name__ == "__main__":
    main()
