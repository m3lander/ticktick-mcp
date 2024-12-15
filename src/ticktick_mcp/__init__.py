"""TickTick MCP Server package."""

from .server import TickTickMCPServer, main
from .utils.auth import AuthConfig, TickTickAuth

__version__ = "0.1.0"
__all__ = ["TickTickMCPServer", "main", "AuthConfig", "TickTickAuth"]