# Geotab MCP Server

This project implements a Model Context Protocol (MCP) server for Geotab APIs. It allows LLMs to access Geotab telematics data through the MCP standard.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your Geotab credentials in `.env` file:
   ```
   GEOTAB_USERNAME=your_username
   GEOTAB_PASSWORD=your_password
   GEOTAB_DATABASE=your_database
   GEOTAB_SERVER=my.geotab.com
   ```

3. Run the server:
   ```bash
   python server.py
   ```

## Available Operations

- `get_device_info`: Get information about devices
- `get_device_location`: Get the current location of devices
- `get_trip_data`: Get trip data for a specific device
- `get_fault_data`: Get fault codes and diagnostic data

## MCP Integration

This server implements the Model Context Protocol specification, allowing LLMs to:
1. Discover available operations
2. Execute operations with appropriate parameters
3. Retrieve structured data from Geotab
