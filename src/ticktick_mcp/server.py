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

from .client import TickTickClient
from .utils.auth import TickTickAuth, AuthConfig
from .resources import TaskResources

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
        self.client = TickTickClient(self.auth)
        self.task_resources = TaskResources(self.client)
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up all MCP protocol handlers."""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available TickTick resources."""
            try:
                return await self.task_resources.list_resources()
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                return []

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a TickTick resource."""
            try:
                return await self.task_resources.read_resource(uri)
            except ValueError as e:
                raise
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                raise

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
            try:
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
            finally:
                await self.client.close()

def main():
    """Entry point for the TickTick MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = TickTickMCPServer()
    asyncio.run(server.run())