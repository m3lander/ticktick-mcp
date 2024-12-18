"""TickTick API client implementation."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import httpx
from pydantic import BaseModel
from cachetools import TTLCache, cached

from ..utils.auth import TickTickAuth, AuthConfig

logger = logging.getLogger(__name__)

class Task(BaseModel):
    """TickTick task model."""
    id: str
    title: str
    content: Optional[str] = None
    project_id: Optional[str] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[int] = None
    priority: Optional[int] = None
    tags: List[str] = []

class Project(BaseModel):
    """TickTick project/list model."""
    id: str
    name: str
    color: Optional[str] = None

class Tag(BaseModel):
    """TickTick tag model."""
    name: str
    label: Optional[str] = None
    color: Optional[str] = None

class TickTickClient:
    """Client for interacting with TickTick API."""

    BASE_URL = "https://api.ticktick.com/api/v2"
    CACHE_TTL = 300  # 5 minutes
    CACHE_MAXSIZE = 100

    def __init__(self, auth: Optional[TickTickAuth] = None):
        """Initialize the TickTick API client."""
        self.auth = auth or TickTickAuth()
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0
        )
        self._cache = TTLCache(maxsize=self.CACHE_MAXSIZE, ttl=self.CACHE_TTL)
        
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        token = await self.auth.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    @cached(cache=TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL))
    async def get_tasks(self, list_id: Optional[str] = None) -> List[Task]:
        """Get tasks, optionally filtered by list ID."""
        headers = await self._get_headers()
        
        if list_id:
            response = await self._client.get(
                f"/project/{list_id}/tasks",
                headers=headers
            )
        else:
            response = await self._client.get(
                "/tasks",
                headers=headers
            )
            
        response.raise_for_status()
        return [Task(**task) for task in response.json()]

    async def get_task(self, task_id: str) -> Task:
        """Get a specific task by ID."""
        headers = await self._get_headers()
        response = await self._client.get(
            f"/task/{task_id}",
            headers=headers
        )
        response.raise_for_status()
        return Task(**response.json())

    async def create_task(self, task: Task) -> Task:
        """Create a new task."""
        headers = await self._get_headers()
        response = await self._client.post(
            "/task",
            headers=headers,
            json=task.dict(exclude_none=True)
        )
        response.raise_for_status()
        self._cache.clear()  # Invalidate cache after creating a task
        return Task(**response.json())

    async def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        headers = await self._get_headers()
        response = await self._client.put(
            f"/task/{task.id}",
            headers=headers,
            json=task.dict(exclude_none=True)
        )
        response.raise_for_status()
        self._cache.clear()  # Invalidate cache after updating a task
        return Task(**response.json())

    async def delete_task(self, task_id: str) -> None:
        """Delete a task."""
        headers = await self._get_headers()
        response = await self._client.delete(
            f"/task/{task_id}",
            headers=headers
        )
        response.raise_for_status()
        self._cache.clear()  # Invalidate cache after deleting a task

    async def complete_task(self, task_id: str) -> Task:
        """Mark a task as completed."""
        headers = await self._get_headers()
        response = await self._client.post(
            f"/task/{task_id}/complete",
            headers=headers
        )
        response.raise_for_status()
        self._cache.clear()  # Invalidate cache after completing a task
        return Task(**response.json())

    @cached(cache=TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL))
    async def get_projects(self) -> List[Project]:
        """Get all projects/lists."""
        headers = await self._get_headers()
        response = await self._client.get(
            "/projects",
            headers=headers
        )
        response.raise_for_status()
        return [Project(**project) for project in response.json()]

    async def search_tasks(self, query: str) -> List[Task]:
        """Search for tasks."""
        headers = await self._get_headers()
        response = await self._client.get(
            "/task/search",
            headers=headers,
            params={"query": query}
        )
        response.raise_for_status()
        return [Task(**task) for task in response.json()]

    @cached(cache=TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL))
    async def get_tags(self) -> List[Tag]:
        """Get all tags."""
        headers = await self._get_headers()
        response = await self._client.get(
            "/tags",
            headers=headers
        )
        response.raise_for_status()
        return [Tag(**tag) for tag in response.json()]

    async def create_tag(self, tag: Tag) -> Tag:
        """Create a new tag."""
        headers = await self._get_headers()
        response = await self._client.post(
            "/tag",
            headers=headers,
            json=tag.dict(exclude_none=True)
        )
        response.raise_for_status()
        self._cache.clear()  # Invalidate cache after creating a tag
        return Tag(**response.json())

    async def update_tag(self, tag: Tag) -> Tag:
        """Update an existing tag."""
        headers = await self._get_headers()
        response = await self._client.put(
            f"/tag/{tag.name}",
            headers=headers,
            json=tag.dict(exclude_none=True)
        )
        response.raise_for_status()
        self._cache.clear()  # Invalidate cache after updating a tag
        return Tag(**response.json())

    async def delete_tag(self, tag_name: str) -> None:
        """Delete a tag."""
        headers = await self._get_headers()
        response = await self._client.delete(
            f"/tag/{tag_name}",
            headers=headers
        )
        response.raise_for_status()
        self._cache.clear()  # Invalidate cache after deleting a tag

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
