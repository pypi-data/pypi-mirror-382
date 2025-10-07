#!/usr/bin/env python
"""
Entry point for running the Crypto MCP Server
This script is designed to be used with Claude Desktop's MCP configuration
"""

import sys
import uvicorn
from crypto_mcp_server.config import settings
from crypto_mcp_server.mcp_server import app


def main():
    """Main entry point for the MCP server"""
    try:
        uvicorn.run(
            app,
            host=settings.mcp_server_host,
            port=settings.mcp_server_port,
            log_level=settings.log_level.lower()
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
