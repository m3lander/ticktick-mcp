# TickTick MCP Server

A Model Context Protocol (MCP) server implementation for TickTick integration. This server allows AI assistants to interact with TickTick for task management, list organization, and productivity workflows.

## Features

- Full TickTick API integration through MCP
- Task management (create, read, update, delete)
- List and project organization
- Natural language task creation
- Template-based workflows
- Secure authentication handling
- Efficient caching

## Installation

```bash
# Install using poetry
poetry install

# Or using pip
pip install .
```

## Configuration

Create a .env file with your TickTick API credentials:

```env
TICKTICK_CLIENT_ID=your_client_id
TICKTICK_CLIENT_SECRET=your_client_secret
```

## Usage

```bash
# Start the MCP server
ticktick-mcp

# Or with custom configuration
ticktick-mcp --config path/to/config.json
```

## Development Status

This project is actively under development. See DEVELOPMENT.md for current status and remaining tasks.

## License

MIT