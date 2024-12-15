"""TickTick MCP Server implementation."""

import asyncio
import logging
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    EmptyResult,
    LoggingLevel
)

from .utils.auth import TickTickAuth, AuthConfig

logger = logging.getLogger("ticktick-mcp")

class TickTickMCPServer:
    """MCP server implementation for TickTick integration."""

    def __init__(self, auth_config: Optional[AuthConfig] = None):
        """Initialize the TickTick MCP server."""
        self.server = Server(
            "ticktick-server",
            version="0.1.0"
        )
        self.auth = TickTickAuth(auth_config)
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up all MCP protocol handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available TickTick resources."""
            # TODO: Implement full resource listing
            return [
                Resource(
                    uri="ticktick://tasks/inbox",
                    name="Inbox Tasks",
                    mimeType="application/json",
                    description="Tasks in your TickTick inbox"
                )
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a TickTick resource."""
            # TODO: Implement resource reading
            if uri == "ticktick://tasks/inbox":
                return '{"tasks": []}'  # Placeholder
            raise ValueError(f"Unknown resource: {uri}")

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available TickTick tools."""
            # TODO: Implement tool listing
            return []

        @self.server.set_logging_level()
        async def set_logging_level(level: LoggingLevel) -> EmptyResult:
            """Set the server's logging level."""
            logger.setLevel(level.upper())
            return EmptyResult()

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as streams:
            read_stream, write_stream = streams
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

def main():
    """Entry point for the TickTick MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = TickTickMCPServer()
    asyncio.run(server.run())