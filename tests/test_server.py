import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from mcp.types import Resource, Tool, TextContent
from mcp.errors import McpError, ErrorCode

from ticktick_mcp.server import TickTickMCPServer
from ticktick_mcp.client import TickTickClient, Task

@pytest.fixture
def mock_client():
    client = AsyncMock(spec=TickTickClient)
    client.get_projects.return_value = [
        MagicMock(id="1", name="Project 1"),
        MagicMock(id="2", name="Project 2")
    ]
    client.get_tasks.return_value = [
        Task(id="1", title="Task 1", content="Content 1"),
        Task(id="2", title="Task 2", content="Content 2")
    ]
    return client

@pytest.fixture
def server(mock_client):
    server = TickTickMCPServer()
    server.client = mock_client
    server.task_resources.client = mock_client
    server.task_tools.client = mock_client
    return server

@pytest.mark.asyncio
async def test_list_resources(server):
    resources = await server.server.handlers["list_resources"]()
    assert len(resources) == 4  # inbox, all, and 2 projects
    assert any(r.uri == "ticktick://tasks/inbox" for r in resources)
    assert any(r.uri == "ticktick://tasks/all" for r in resources)
    assert any(r.uri == "ticktick://tasks/project/1" for r in resources)
    assert any(r.uri == "ticktick://tasks/project/2" for r in resources)

@pytest.mark.asyncio
async def test_read_resource(server):
    uri = "ticktick://tasks/all"
    result = await server.server.handlers["read_resource"](uri)
    tasks = json.loads(result)
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 1"
    assert tasks[1]["title"] == "Task 2"

@pytest.mark.asyncio
async def test_list_tools(server):
    tools = await server.server.handlers["list_tools"]()
    assert len(tools) == 5
    tool_names = [t.name for t in tools]
    assert "create_task" in tool_names
    assert "update_task" in tool_names
    assert "complete_task" in tool_names
    assert "delete_task" in tool_names
    assert "search_tasks" in tool_names

@pytest.mark.asyncio
async def test_call_tool_create_task(server):
    server.client.create_task.return_value = Task(id="3", title="New Task", content="New Content")
    result = await server.server.handlers["call_tool"]("create_task", {"title": "New Task", "content": "New Content"})
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    task_dict = json.loads(result[0].text)
    assert task_dict["title"] == "New Task"
    assert task_dict["content"] == "New Content"

@pytest.mark.asyncio
async def test_call_tool_unknown_tool(server):
    with pytest.raises(McpError) as exc_info:
        await server.server.handlers["call_tool"]("unknown_tool", {})
    assert exc_info.value.code == ErrorCode.MethodNotFound

@pytest.mark.asyncio
async def test_set_logging_level(server):
    result = await server.server.handlers["set_logging_level"]("DEBUG")
    assert isinstance(result, dict)
    assert len(result) == 0  # EmptyResult

@pytest.mark.asyncio
async def test_caching_get_tasks(server):
    # First call
    await server.client.get_tasks()
    assert server.client.get_tasks.call_count == 1

    # Second call (should use cache)
    await server.client.get_tasks()
    assert server.client.get_tasks.call_count == 1

    # Call with different argument (should not use cache)
    await server.client.get_tasks(list_id="1")
    assert server.client.get_tasks.call_count == 2

@pytest.mark.asyncio
async def test_cache_invalidation(server):
    # Populate cache
    await server.client.get_tasks()
    assert server.client.get_tasks.call_count == 1

    # Create a new task (should invalidate cache)
    new_task = Task(id="3", title="New Task", content="New Content")
    await server.client.create_task(new_task)

    # Get tasks again (should not use cache)
    await server.client.get_tasks()
    assert server.client.get_tasks.call_count == 2

if __name__ == "__main__":
    pytest.main()
