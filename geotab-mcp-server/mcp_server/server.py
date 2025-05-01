"""MCP server implementation for Geotab APIs."""
import os
import json
import logging
from typing import Dict, Any, List, Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .models import (
    MCPDiscoverRequest, 
    MCPDiscoverResponse, 
    MCPExecuteRequest, 
    MCPExecuteResponse, 
    MCPErrorResponse,
    MCPOperation,
    MCPParameter
)
from .operations import GeotabOperations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp-server")

# Initialize the FastAPI app
app = FastAPI(
    title="Geotab MCP Server",
    description="Model Context Protocol server for Geotab APIs",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Geotab operations
geotab_ops = GeotabOperations()

# MCP version
MCP_VERSION = "0.1.0"

# Operation definitions for MCP discover
OPERATIONS = [
    MCPOperation(
        name="get_device_info",
        description="Get information about all devices in the Geotab account",
        parameters=[
            MCPParameter(
                name="include_inactive",
                type="boolean",
                description="Whether to include inactive devices in the results",
                required=False,
                default=False
            )
        ],
        returns="A list of devices with their properties and status information"
    ),
    MCPOperation(
        name="get_device_location",
        description="Get the current location of a specific device",
        parameters=[
            MCPParameter(
                name="device_id",
                type="string",
                description="ID of the device to get location for",
                required=True
            )
        ],
        returns="Current location information including coordinates, speed, and address"
    ),
    MCPOperation(
        name="get_trip_data",
        description="Get trip data for a specific device within a time range",
        parameters=[
            MCPParameter(
                name="device_id",
                type="string",
                description="ID of the device to get trip data for",
                required=True
            ),
            MCPParameter(
                name="days",
                type="integer",
                description="Number of days to look back from current time",
                required=False,
                default=1
            )
        ],
        returns="List of trips with start/end locations, distance, duration, and other metrics"
    ),
    MCPOperation(
        name="get_fault_data",
        description="Get fault codes and diagnostic data for a device",
        parameters=[
            MCPParameter(
                name="device_id",
                type="string",
                description="ID of the device to get fault data for",
                required=True
            ),
            MCPParameter(
                name="days",
                type="integer",
                description="Number of days to look back from current time",
                required=False,
                default=7
            ),
            MCPParameter(
                name="active_only",
                type="boolean",
                description="Whether to include only active faults",
                required=False,
                default=False
            )
        ],
        returns="List of fault codes with diagnostic information, timestamps, and status"
    )
]


@app.post("/mcp", response_class=JSONResponse)
async def mcp_endpoint(request: Request) -> Dict[str, Any]:
    """Main MCP endpoint that handles discover and execute requests."""
    try:
        # Parse the incoming JSON
        data = await request.json()
        
        # Log the request
        logger.info(f"Received MCP request: {json.dumps(data)}")
        
        # Handle by request type
        request_type = data.get("type")
        
        if request_type == "discover":
            return await handle_discover(MCPDiscoverRequest(**data))
        elif request_type == "execute":
            return await handle_execute(MCPExecuteRequest(**data))
        else:
            error_response = MCPErrorResponse(
                version=MCP_VERSION,
                error="Invalid request type",
                details={"supported_types": ["discover", "execute"]}
            )
            return error_response.dict()
            
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        error_response = MCPErrorResponse(
            version=MCP_VERSION,
            error="Invalid request format",
            details={"validation_errors": e.errors()}
        )
        return error_response.dict()
        
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        error_response = MCPErrorResponse(
            version=MCP_VERSION,
            error="Server error",
            details={"message": str(e)}
        )
        return error_response.dict()


async def handle_discover(request: MCPDiscoverRequest) -> Dict[str, Any]:
    """Handle MCP discover requests."""
    logger.info(f"Processing discover request with version {request.version}")
    
    # Create the discover response
    response = MCPDiscoverResponse(
        version=MCP_VERSION,
        operations=OPERATIONS
    )
    
    return response.dict()


async def handle_execute(request: MCPExecuteRequest) -> Dict[str, Any]:
    """Handle MCP execute requests."""
    logger.info(f"Processing execute request for operation {request.operation}")
    
    # Check if the operation exists
    if request.operation not in geotab_ops.operation_map:
        error_response = MCPErrorResponse(
            version=MCP_VERSION,
            error="Unknown operation",
            details={
                "requested_operation": request.operation,
                "available_operations": list(geotab_ops.operation_map.keys())
            }
        )
        return error_response.dict()
    
    try:
        # Get the operation method
        operation_method = geotab_ops.operation_map[request.operation]
        
        # Execute the operation with parameters
        result = await operation_method(geotab_ops, **request.parameters)
        
        # Create the execute response
        response = MCPExecuteResponse(
            version=MCP_VERSION,
            operation=request.operation,
            result=result["result"]
        )
        
        return response.dict()
        
    except TypeError as e:
        logger.error(f"Parameter error for operation {request.operation}: {e}")
        error_response = MCPErrorResponse(
            version=MCP_VERSION,
            error="Invalid parameters",
            details={"message": str(e)}
        )
        return error_response.dict()
        
    except Exception as e:
        logger.error(f"Error executing operation {request.operation}: {e}", exc_info=True)
        error_response = MCPErrorResponse(
            version=MCP_VERSION,
            error="Operation execution failed",
            details={"message": str(e)}
        )
        return error_response.dict()
