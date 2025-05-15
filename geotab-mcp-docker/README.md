# Geotab MCP Server for Claude

This repository contains a Docker-based implementation of the Model Context Protocol (MCP) server for Geotab APIs. It provides an easy way to allow Claude to interact with Geotab telematics data through a standardized protocol.

## What is MCP?

The Model Context Protocol (MCP) is a standardized way for large language models (LLMs) like Claude to interact with external APIs and data sources. It allows LLMs to:

1. **Discover** available operations without hardcoding knowledge about the API
2. **Execute** operations with appropriate parameters
3. Process structured **results** in a consistent format

## Features

This MCP server provides access to the following Geotab APIs:

- **Device Management**: List all vehicles/devices in your Geotab account
- **Real-time Location**: Get current location of any device with address information
- **Trip History**: View trips with start/end locations, distance, duration
- **Fault Diagnostics**: Check diagnostic trouble codes and fault data
- **Status Data**: Access telemetry data like engine metrics

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Geotab account with API credentials

### Setup

1. **Clone this repository**

```bash
git clone https://github.com/yourusername/geotab-mcp-docker.git
cd geotab-mcp-docker
```

2. **Configure your Geotab credentials**

Copy `.env.example` to `.env` and edit it to include your Geotab credentials:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Fill in your credentials:

```
GEOTAB_USERNAME=your_username
GEOTAB_PASSWORD=your_password
GEOTAB_DATABASE=your_database
GEOTAB_SERVER=my.geotab.com
```

3. **Build and start the Docker container**

```bash
docker-compose up -d
```

4. **Verify the server is running**

```bash
curl http://localhost:8000/
```

You should see basic information about the MCP server.

### Testing with the Example Client

The `examples` directory contains a simple client for testing the MCP server:

```bash
# Discover available operations
python examples/mcp_client.py

# Execute an operation (list devices)
python examples/mcp_client.py --operation get_devices

# Get location of a specific device
python examples/mcp_client.py --operation get_device_location --params '{"device_id": "b1"}'

# Get trips for a device over the last 7 days
python examples/mcp_client.py --operation get_trips --params '{"device_id": "b1", "days": 7}'
```

## Integrating with Claude

To enable Claude to use this MCP server, you need to configure it as a tool in Claude's interface.

### Option 1: Claude Web Interface

1. Log in to [Claude](https://claude.ai/)
2. Start a new conversation
3. Click on the "+" icon next to the input field to add a tool
4. Select "Create new tool" or "Add new tool" option
5. Configure the tool with the following settings:
   - **Tool name**: Geotab Fleet Management
   - **Tool type**: MCP
   - **Endpoint URL**: `http://your-server-address:8000/mcp` (replace with your actual server address)
   - **Authentication**: If your server requires authentication, add any necessary headers
   - **Description**: Access Geotab telematics data including vehicle locations, trips, diagnostic trouble codes, and engine metrics.

### Option 2: Claude API

If you're using Claude through the API, you can configure the tool in your API requests:

```json
{
  "model": "claude-3-opus-20240229",
  "max_tokens": 4096,
  "temperature": 0.7,
  "messages": [
    {"role": "user", "content": "Which vehicles in our fleet are currently active?"}
  ],
  "tools": [
    {
      "name": "geotab_fleet_management",
      "type": "mcp",
      "endpoint": "http://your-server-address:8000/mcp",
      "description": "Access Geotab telematics data including vehicle locations, trips, diagnostic trouble codes, and engine metrics."
    }
  ]
}
```

### Prompting Claude

Once the tool is configured, Claude can use it to answer questions about your Geotab data. Here are some example prompts:

- "Show me all the active vehicles in our fleet."
- "Where is vehicle B1 located right now?"
- "What trips did vehicle G7 make in the last 3 days?"
- "Are there any active fault codes for our delivery truck with ID T4?"
- "What was the average speed of vehicle V9 during its last trip?"
- "Compare the fuel usage efficiency between vehicles in our fleet."

Claude will automatically:
1. Discover the available operations on your MCP server
2. Choose the appropriate operation based on the question
3. Execute the operation with the right parameters
4. Process and explain the results in natural language

## Advanced Configuration

### Server Security

For production environments, consider implementing:

1. **API Key Authentication**:
   - Add an authentication middleware to your FastAPI app
   - Configure Claude with the appropriate headers

2. **HTTPS**:
   - Set up a reverse proxy (like Nginx) with SSL
   - Use Let's Encrypt for free SSL certificates
   - Update the endpoint URL in Claude to use `https://`

3. **Firewalls**:
   - Restrict access to your server by IP address
   - Only allow traffic from Anthropic's IP addresses

### Customizing Operations

To add custom operations or modify existing ones, edit the following files:

- `mcp/operations.py`: Define new operations and their parameters
- `geotab/client.py`: Add methods to interact with additional Geotab APIs

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify your Geotab credentials in the `.env` file
   - Make sure your API user has sufficient permissions

2. **Connection Issues**:
   - Check that your server is accessible from the internet if hosted locally
   - Verify firewall rules allow incoming connections on port 8000

3. **Rate Limiting**:
   - Geotab may rate-limit API requests
   - Consider implementing caching for frequently accessed data

### Viewing Logs

```bash
# View server logs
docker-compose logs -f

# Check a specific log file
docker-compose exec mcp-server cat logs/mcp_server.log
```

## API Reference

For more information on the Geotab API, see the [MyGeotab SDK Documentation](https://geotab.github.io/sdk/).

For more information on the Model Context Protocol, see the [MCP Specification](https://modelcontextprotocol.io/llms-full.txt).

## License

MIT
