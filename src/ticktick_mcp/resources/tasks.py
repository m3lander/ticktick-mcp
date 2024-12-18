"""Task resource handlers."""

import json
import logging
from typing import List
from urllib.parse import unquote

from mcp.types import Resource, ResourceTemplate
from mcp.errors import McpError, ErrorCode

from ..client import TickTickClient

logger = logging.getLogger(__name__)

class TaskResources:
    """Task resource handlers."""

    def __init__(self, client: TickTickClient):
        """Initialize task resources."""
        self.client = client

    async def list_resources(self) -> List[Resource]:
        """List available task resources."""
        resources = [
            Resource(
                uri="ticktick://tasks/inbox",
                name="Inbox Tasks",
                mimeType="application/json",
                description="Tasks in your TickTick inbox"
            ),
            Resource(
                uri="ticktick://tasks/all",
                name="All Tasks",
                mimeType="application/json",
                description="All your TickTick tasks"
            )
        ]

        # Add project-specific task resources
        try:
            projects = await self.client.get_projects()
            for project in projects:
                resources.append(
                    Resource(
                        uri=f"ticktick://tasks/project/{project.id}",
                        name=f"Tasks in {project.name}",
                        mimeType="application/json",
                        description=f"Tasks in the {project.name} project"
                    )
                )
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")

        return resources

    async def list_resource_templates(self) -> List[ResourceTemplate]:
        """List available resource templates."""
        return [
            ResourceTemplate(
                uriTemplate="ticktick://tasks/search/{query}",
                name="Search Tasks",
                mimeType="application/json",
                description="Search for tasks using a query string"
            )
        ]

    async def read_resource(self, uri: str) -> str:
        """Read a task resource."""
        try:
            if uri == "ticktick://tasks/all":
                tasks = await self.client.get_tasks()
                return json.dumps([task.dict() for task in tasks])
            
            if uri == "ticktick://tasks/inbox":
                # Inbox tasks typically have no project ID
                tasks = await self.client.get_tasks()
                inbox_tasks = [task for task in tasks if not task.project_id]
                return json.dumps([task.dict() for task in inbox_tasks])
            
            if uri.startswith("ticktick://tasks/project/"):
                project_id = uri.split("/")[-1]
                tasks = await self.client.get_tasks(list_id=project_id)
                return json.dumps([task.dict() for task in tasks])

            if uri.startswith("ticktick://tasks/search/"):
                query = unquote(uri.split("/")[-1])
                tasks = await self.client.search_tasks(query)
                return json.dumps([task.dict() for task in tasks])

            raise McpError(ErrorCode.InvalidRequest, f"Unknown resource: {uri}")
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            raise McpError(ErrorCode.InternalError, f"Error reading resource: {str(e)}")

    async def subscribe_resource(self, uri: str) -> None:
        """Subscribe to a resource for updates."""
        # This method can be implemented if real-time updates are needed
        # For now, we'll just log the subscription request
        logger.info(f"Subscription requested for resource: {uri}")

    async def unsubscribe_resource(self, uri: str) -> None:
        """Unsubscribe from a resource."""
        # This method can be implemented if real-time updates are needed
        # For now, we'll just log the unsubscription request
        logger.info(f"Unsubscription requested for resource: {uri}")
