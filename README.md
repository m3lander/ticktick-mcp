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
pip install -r requirements.txt
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

# Or using Python directly
python -m ticktick_mcp
```

## Development

### Setting up the development environment

1. Clone the repository:
   ```
   git clone https://github.com/your-username/ticktick-mcp.git
   cd ticktick-mcp
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up pre-commit hooks:
   ```
   pip install pre-commit
   pre-commit install
   ```

### Running tests

To run the test suite:

```bash
pytest
```

### Code Style

We use Black for code formatting. To check your code style:

```bash
black --check .
```

To automatically format your code:

```bash
black .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgements

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [TickTick API](https://developer.ticktick.com/)
