"""OAuth2 implementation for TickTick."""

import base64
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class OAuth2Token(BaseModel):
    """OAuth2 token model."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: datetime = datetime.now()

    @property
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        expiry = self.created_at + timedelta(seconds=self.expires_in)
        return datetime.now() >= expiry

class OAuth2Handler:
    """Handles OAuth2 authentication flow for TickTick."""

    AUTH_URL = "https://ticktick.com/oauth/authorize"
    TOKEN_URL = "https://ticktick.com/oauth/token"
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[str] = None,
        scope: str = "tasks:write tasks:read",
    ):
        """Initialize OAuth2 handler."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self._client = httpx.AsyncClient()
        self._token: Optional[OAuth2Token] = None

    async def get_authorization_url(self) -> str:
        """Get the authorization URL for the OAuth2 flow."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": self.scope
        }
        if self.redirect_uri:
            params["redirect_uri"] = self.redirect_uri
            
        return f"{self.AUTH_URL}?{httpx.QueryParams(params)}"

    async def fetch_token(self, code: str) -> OAuth2Token:
        """Exchange authorization code for access token."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        if self.redirect_uri:
            data["redirect_uri"] = self.redirect_uri

        async with self._client as client:
            response = await client.post(
                self.TOKEN_URL,
                data=data,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            self._token = OAuth2Token(**response.json())
            return self._token

    async def refresh_token(self, refresh_token: str) -> OAuth2Token:
        """Refresh an expired access token."""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        async with self._client as client:
            response = await client.post(
                self.TOKEN_URL,
                data=data,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            self._token = OAuth2Token(**response.json())
            return self._token

    def save_token(self, path: str):
        """Save token to a file."""
        if self._token:
            with open(path, "w") as f:
                json.dump(
                    self._token.dict(),
                    f,
                    default=str
                )

    def load_token(self, path: str) -> Optional[OAuth2Token]:
        """Load token from a file."""
        try:
            with open(path) as f:
                data = json.load(f)
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                self._token = OAuth2Token(**data)
                return self._token
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    async def get_valid_token(self) -> Optional[OAuth2Token]:
        """Get a valid token, refreshing if necessary."""
        if not self._token:
            return None
            
        if not self._token.is_expired:
            return self._token
            
        if self._token.refresh_token:
            return await self.refresh_token(self._token.refresh_token)
            
        return None