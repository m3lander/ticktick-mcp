"""Task management tools."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from mcp.types import Tool, TextContent
from pydantic import BaseModel

from ..client import TickTickClient, Task

logger = logging.getLogger(__name__)

class CreateTaskInput(BaseModel):
    """Input schema for task creation."""
    title: str
    content: str | None = None
    project_id: str | None = None
    due_date: datetime | None = None
    tags: List[str] = []

class UpdateTaskInput(BaseModel):
    """Input schema for task updates."""
    task_id: str
    title: str | None = None
    content: str | None = None
    project_id: str | None = None
    due_date: datetime | None = None
    tags: List[str] | None = None

class TaskTools:
    """Task management tools."""

    def __init__(self, client: TickTickClient):
        """Initialize task tools."""
        self.client = client

    def get_tools(self) -> List[Tool]:
        """Get available task tools."""
        return [
            Tool(
                name="create_task",
                description="Create a new task in TickTick",
                inputSchema=CreateTaskInput.schema()
            ),
            Tool(
                name="update_task",
                description="Update an existing task",
                inputSchema=UpdateTaskInput.schema()
            ),
            Tool(
                name="complete_task",
                description="Mark a task as complete",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="delete_task",
                description="Delete a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="search_tasks",
                description="Search for tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            )
        ]

    async def create_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new task."""
        input_data = CreateTaskInput(**args)
        task = Task(
            title=input_data.title,
            content=input_data.content,
            project_id=input_data.project_id,
            due_date=input_data.due_date,
            tags=input_data.tags
        )
        
        try:
            created_task = await self.client.create_task(task)
            return [TextContent(
                type="text",
                text=json.dumps(created_task.dict(), default=str)
            )]
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return [TextContent(
                type="text",
                text=f"Error creating task: {str(e)}"
            )]

    async def update_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Update an existing task."""
        input_data = UpdateTaskInput(**args)
        
        try:
            # First get existing task
            current_task = await self.client.get_task(input_data.task_id)
            
            # Update with new values
            update_data = input_data.dict(exclude_none=True)
            for key, value in update_data.items():
                if key != 'task_id':
                    setattr(current_task, key, value)
            
            updated_task = await self.client.update_task(current_task)
            return [TextContent(
                type="text",
                text=json.dumps(updated_task.dict(), default=str)
            )]
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return [TextContent(
                type="text",
                text=f"Error updating task: {str(e)}"
            )]

    async def complete_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Mark a task as complete."""
        task_id = args["task_id"]
        
        try:
            task = await self.client.get_task(task_id)
            task.status = 2  # Completed status
            updated_task = await self.client.update_task(task)
            return [TextContent(
                type="text",
                text=f"Task '{updated_task.title}' marked as complete."
            )]
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return [TextContent(
                type="text",
                text=f"Error completing task: {str(e)}"
            )]

    async def delete_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Delete a task."""
        task_id = args["task_id"]
        
        try:
            await self.client.delete_task(task_id)
            return [TextContent(
                type="text",
                text=f"Task {task_id} deleted successfully."
            )]
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return [TextContent(
                type="text",
                text=f"Error deleting task: {str(e)}"
            )]

    async def search_tasks(self, args: Dict[str, Any]) -> List[TextContent]:
        """Search for tasks."""
        query = args["query"]
        
        try:
            tasks = await self.client.search_tasks(query)
            return [TextContent(
                type="text",
                text=json.dumps([t.dict() for t in tasks], default=str)
            )]
        except Exception as e:
            logger.error(f"Error searching tasks: {e}")
            return [TextContent(
                type="text",
                text=f"Error searching tasks: {str(e)}"
            )]