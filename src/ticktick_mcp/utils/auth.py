"""Authentication utilities for TickTick MCP server."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import os
from typing import Optional

import httpx
from cachetools import TTLCache


@dataclass
class AuthConfig:
    """Authentication configuration."""
    client_id: str
    client_secret: str
    token_expiry: timedelta = timedelta(hours=1)


class TickTickAuth:
    """Handles TickTick authentication and token management."""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        """Initialize auth handler with optional config."""
        if config is None:
            # Load from environment if no config provided
            config = AuthConfig(
                client_id=os.environ["TICKTICK_CLIENT_ID"],
                client_secret=os.environ["TICKTICK_CLIENT_SECRET"],
            )
        self.config = config
        self._token_cache = TTLCache(maxsize=1, ttl=3600)  # 1 hour TTL
        self._client = httpx.AsyncClient()

    async def get_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if "access_token" in self._token_cache:
            return self._token_cache["access_token"]

        # TODO: Implement actual OAuth2 flow
        # For now, just return the client ID as a placeholder
        self._token_cache["access_token"] = self.config.client_id
        return self._token_cache["access_token"]

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()