"""Task management tools."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

from ..client import TickTickClient, Task, Tag

logger = logging.getLogger(__name__)

class CreateTaskInput(BaseModel):
    """Input schema for task creation."""
    title: str
    content: str | None = None
    project_id: str | None = None
    due_date: datetime | None = None
    tags: List[str] = Field(default_factory=list)

class UpdateTaskInput(BaseModel):
    """Input schema for task updates."""
    task_id: str
    title: str | None = None
    content: str | None = None
    project_id: str | None = None
    due_date: datetime | None = None
    tags: List[str] | None = None

class CompleteTaskInput(BaseModel):
    """Input schema for completing a task."""
    task_id: str

class DeleteTaskInput(BaseModel):
    """Input schema for deleting a task."""
    task_id: str

class SearchTasksInput(BaseModel):
    """Input schema for searching tasks."""
    query: str

class CreateTagInput(BaseModel):
    """Input schema for tag creation."""
    name: str
    label: str | None = None
    color: str | None = None

class UpdateTagInput(BaseModel):
    """Input schema for tag updates."""
    name: str
    label: str | None = None
    color: str | None = None

class DeleteTagInput(BaseModel):
    """Input schema for deleting a tag."""
    name: str

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
                inputSchema=CompleteTaskInput.schema()
            ),
            Tool(
                name="delete_task",
                description="Delete a task",
                inputSchema=DeleteTaskInput.schema()
            ),
            Tool(
                name="search_tasks",
                description="Search for tasks",
                inputSchema=SearchTasksInput.schema()
            ),
            Tool(
                name="get_tags",
                description="Get all tags",
                inputSchema={}
            ),
            Tool(
                name="create_tag",
                description="Create a new tag",
                inputSchema=CreateTagInput.schema()
            ),
            Tool(
                name="update_tag",
                description="Update an existing tag",
                inputSchema=UpdateTagInput.schema()
            ),
            Tool(
                name="delete_tag",
                description="Delete a tag",
                inputSchema=DeleteTagInput.schema()
            )
        ]

    async def create_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new task."""
        try:
            input_data = CreateTaskInput(**args)
            task = Task(
                title=input_data.title,
                content=input_data.content,
                project_id=input_data.project_id,
                due_date=input_data.due_date,
                tags=input_data.tags
            )
            
            created_task = await self.client.create_task(task)
            return [TextContent(
                type="text",
                text=json.dumps(created_task.dict(), default=str)
            )]
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return [TextContent(
                type="text",
                text=f"Error creating task: {str(e)}",
                isError=True
            )]

    async def update_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Update an existing task."""
        try:
            input_data = UpdateTaskInput(**args)
            
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
                text=f"Error updating task: {str(e)}",
                isError=True
            )]

    async def complete_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Mark a task as complete."""
        try:
            input_data = CompleteTaskInput(**args)
            completed_task = await self.client.complete_task(input_data.task_id)
            return [TextContent(
                type="text",
                text=f"Task '{completed_task.title}' marked as complete."
            )]
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return [TextContent(
                type="text",
                text=f"Error completing task: {str(e)}",
                isError=True
            )]

    async def delete_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Delete a task."""
        try:
            input_data = DeleteTaskInput(**args)
            await self.client.delete_task(input_data.task_id)
            return [TextContent(
                type="text",
                text=f"Task {input_data.task_id} deleted successfully."
            )]
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return [TextContent(
                type="text",
                text=f"Error deleting task: {str(e)}",
                isError=True
            )]

    async def search_tasks(self, args: Dict[str, Any]) -> List[TextContent]:
        """Search for tasks."""
        try:
            input_data = SearchTasksInput(**args)
            tasks = await self.client.search_tasks(input_data.query)
            return [TextContent(
                type="text",
                text=json.dumps([t.dict() for t in tasks], default=str)
            )]
        except Exception as e:
            logger.error(f"Error searching tasks: {e}")
            return [TextContent(
                type="text",
                text=f"Error searching tasks: {str(e)}",
                isError=True
            )]

    async def get_tags(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get all tags."""
        try:
            tags = await self.client.get_tags()
            return [TextContent(
                type="text",
                text=json.dumps([t.dict() for t in tags], default=str)
            )]
        except Exception as e:
            logger.error(f"Error getting tags: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting tags: {str(e)}",
                isError=True
            )]

    async def create_tag(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new tag."""
        try:
            input_data = CreateTagInput(**args)
            tag = Tag(
                name=input_data.name,
                label=input_data.label,
                color=input_data.color
            )
            created_tag = await self.client.create_tag(tag)
            return [TextContent(
                type="text",
                text=json.dumps(created_tag.dict(), default=str)
            )]
        except Exception as e:
            logger.error(f"Error creating tag: {e}")
            return [TextContent(
                type="text",
                text=f"Error creating tag: {str(e)}",
                isError=True
            )]

    async def update_tag(self, args: Dict[str, Any]) -> List[TextContent]:
        """Update an existing tag."""
        try:
            input_data = UpdateTagInput(**args)
            tag = Tag(
                name=input_data.name,
                label=input_data.label,
                color=input_data.color
            )
            updated_tag = await self.client.update_tag(tag)
            return [TextContent(
                type="text",
                text=json.dumps(updated_tag.dict(), default=str)
            )]
        except Exception as e:
            logger.error(f"Error updating tag: {e}")
            return [TextContent(
                type="text",
                text=f"Error updating tag: {str(e)}",
                isError=True
            )]

    async def delete_tag(self, args: Dict[str, Any]) -> List[TextContent]:
        """Delete a tag."""
        try:
            input_data = DeleteTagInput(**args)
            await self.client.delete_tag(input_data.name)
            return [TextContent(
                type="text",
                text=f"Tag '{input_data.name}' deleted successfully."
            )]
        except Exception as e:
            logger.error(f"Error deleting tag: {e}")
            return [TextContent(
                type="text",
                text=f"Error deleting tag: {str(e)}",
                isError=True
            )]
