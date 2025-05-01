# Integrating Geotab MCP Server with LLMs

This document explains how to integrate the Geotab MCP Server with Language Models (LLMs) following the Model Context Protocol (MCP).

## What is MCP?

The Model Context Protocol (MCP) enables Language Models to access external tools and data sources in a standardized way. It allows LLMs to:

1. Discover what operations are available
2. Execute operations with appropriate parameters
3. Process structured results

## Setup for LLM Integration

### 1. Server Configuration

Make sure your Geotab MCP Server is running and accessible. By default, it runs on:

```
http://localhost:8000/mcp
```

### 2. LLM Connection

When connecting an LLM to the Geotab MCP Server, you need to provide:

- The MCP server endpoint URL
- Instructions on how to use the MCP protocol
- Context about what Geotab data is available

## Example LLM Prompt

Here's an example prompt template for instructing an LLM to use the Geotab MCP Server:

```
You are a helpful assistant with access to Geotab telematics data through an MCP server.

To access data, follow these steps:

1. DISCOVER available operations:
   Send a request to the MCP server with:
   {
     "type": "discover",
     "version": "0.1.0"
   }

2. EXECUTE operations by sending:
   {
     "type": "execute",
     "version": "0.1.0",
     "operation": "<operation_name>",
     "parameters": {
       "<param1>": <value1>,
       "<param2>": <value2>
     }
   }

3. Process the RESULT which will be in this format:
   {
     "type": "execute",
     "version": "0.1.0", 
     "operation": "<operation_name>",
     "result": {
       // Operation-specific result data
     }
   }

When answering questions about fleet data, you should:
1. Discover what operations are available
2. Execute the appropriate operation(s) based on the question
3. Process the results and provide a clear answer

The MCP server endpoint is: http://localhost:8000/mcp
```

## Example Interactions

### Discovering Operations

```
Human: What Geotab data can you access?