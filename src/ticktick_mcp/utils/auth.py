"""Authentication utilities for TickTick MCP server."""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import logging

from .oauth import OAuth2Handler, OAuth2Token

logger = logging.getLogger(__name__)

@dataclass
class AuthConfig:
    """Authentication configuration."""
    client_id: str
    client_secret: str
    token_path: str = os.path.expanduser("~/.ticktick/token.json")
    redirect_uri: Optional[str] = None
    scope: str = "tasks:write tasks:read"

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
        
        # Ensure token directory exists
        os.makedirs(os.path.dirname(config.token_path), exist_ok=True)
        
        self.oauth = OAuth2Handler(
            client_id=config.client_id,
            client_secret=config.client_secret,
            redirect_uri=config.redirect_uri,
            scope=config.scope
        )

    async def get_token(self) -> str:
        """Get a valid access token."""
        # Try to load existing token
        token = self.oauth.load_token(self.config.token_path)
        
        if token and not token.is_expired:
            return token.access_token
            
        if token and token.refresh_token:
            try:
                token = await self.oauth.refresh_token(token.refresh_token)
                self.oauth.save_token(self.config.token_path)
                return token.access_token
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
        
        # If we get here, we need a new token
        auth_url = await self.oauth.get_authorization_url()
        raise ValueError(
            f"No valid token found. Please authorize at: {auth_url}"
        )

    async def handle_oauth_callback(self, code: str) -> OAuth2Token:
        """Handle OAuth callback with authorization code."""
        token = await self.oauth.fetch_token(code)
        self.oauth.save_token(self.config.token_path)
        return token