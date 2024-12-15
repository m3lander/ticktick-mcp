# TickTick MCP Server

A Model Context Protocol (MCP) server implementation for TickTick integration. This server allows AI assistants to interact with TickTick for task management, list organization, and productivity workflows.

## Features

- Full TickTick API integration through MCP
- Task management (create, read, update, delete)
- List and project organization
- OAuth2 authentication handling
- Efficient caching
- Comprehensive logging

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ticktick-mcp.git
cd ticktick-mcp

# Install using poetry (recommended)
poetry install

# Or using pip
pip install .
```

## Configuration

1. Create a TickTick Developer Application:
   - Go to TickTick Developer settings
   - Create a new application
   - Note your Client ID and Client Secret

2. Create a `.env` file with your credentials:

```env
TICKTICK_CLIENT_ID=your_client_id
TICKTICK_CLIENT_SECRET=your_client_secret
```

3. First run will prompt for OAuth2 authorization:
   - Follow the authorization URL
   - Grant access to your TickTick account
   - Copy the authorization code
   - The server will handle token management automatically

## Usage

### Starting the Server

```bash
# Using poetry
poetry run ticktick-mcp

# Or using the installed script
ticktick-mcp
```

### Available Resources

- `ticktick://tasks/all` - All tasks
- `ticktick://tasks/inbox` - Inbox tasks
- `ticktick://tasks/project/{id}` - Tasks in a specific project
- `ticktick://tasks/search/{query}` - Search results

### Available Tools

- `create_task` - Create a new task
- `update_task` - Update an existing task
- `complete_task` - Mark a task as complete
- `delete_task` - Delete a task
- `search_tasks` - Search for tasks

## Development

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .
```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:
1. Delete the token file at `~/.ticktick/token.json`
2. Restart the server
3. Follow the OAuth2 authorization flow again

### Logging

The server logs to stderr with detailed information about operations and errors. Set the log level using the `LOG_LEVEL` environment variable or through the MCP protocol.

## License

MIT