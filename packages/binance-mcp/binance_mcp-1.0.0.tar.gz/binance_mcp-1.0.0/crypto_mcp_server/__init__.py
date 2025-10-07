"""
Crypto MCP Server - Model Context Protocol server for crypto trading via Binance.US
"""

__version__ = "1.0.0"

from crypto_mcp_server.mcp_server import app
from crypto_mcp_server.config import settings

__all__ = ["app", "settings"]
