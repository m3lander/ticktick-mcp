"""Task resource handlers."""

import json
import logging
from typing import List

from mcp.types import Resource

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

    async def read_resource(self, uri: str) -> str:
        """Read a task resource."""
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
            query = uri.split("/")[-1]
            tasks = await self.client.search_tasks(query)
            return json.dumps([task.dict() for task in tasks])

        raise ValueError(f"Unknown resource: {uri}")
