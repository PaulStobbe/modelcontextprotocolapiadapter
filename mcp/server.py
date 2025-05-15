"""
FastAPI implementation of the MCP server for Geotab.
"""
import json
import logging
from typing import Dict, Any, Union

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    MCP_VERSION,
    MCPDiscoverRequest,
    MCPExecuteRequest,
    MCPDiscoverResponse,
    MCPExecuteResponse,
    MCPErrorResponse
)
from .operations import OPERATIONS, execute_operation

# Configure logging
logger = logging.getLogger("mcp.server")

# Create FastAPI app
app = FastAPI(
    title="Geotab MCP Server",
    description="Model Context Protocol server for Geotab APIs",
    version=MCP_VERSION
)

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/mcp")
async def mcp_endpoint(request: Request) -> Dict[str, Any]:
    """
    Main MCP endpoint that handles both discover and execute requests.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        MCP response as a dictionary
    """
    try:
        # Parse the request JSON
        body = await request.json()
        logger.info(f"Received MCP request: {body}")
        
        # Process based on request type
        request_type = body.get("type")
        
        if request_type == "discover":
            return await handle_discover(body)
        elif request_type == "execute":
            return await handle_execute(body)
        else:
            # Invalid request type
            error_response = MCPErrorResponse(
                version=MCP_VERSION,
                error="Invalid request type",
                details={"message": f"Unsupported request type: {request_type}"}
            )
            return error_response.dict()
    
    except json.JSONDecodeError:
        # Invalid JSON
        logger.error("Invalid JSON in request body")
        error_response = MCPErrorResponse(
            version=MCP_VERSION,
            error="Invalid JSON",
            details={"message": "Request body is not valid JSON"}
        )
        return error_response.dict()
    
    except Exception as e:
        # Unexpected error
        logger.error(f"Error processing request: {e}", exc_info=True)
        error_response = MCPErrorResponse(
            version=MCP_VERSION,
            error="Server error",
            details={"message": str(e)}
        )
        return error_response.dict()


async def handle_discover(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle an MCP discover request.
    
    Args:
        body: The request body as a dictionary
        
    Returns:
        Discover response as a dictionary
    """
    try:
        request = MCPDiscoverRequest(**body)
        request.validate_type()
        
        # Create response with all available operations
        response = MCPDiscoverResponse(
            version=MCP_VERSION,
            operations=OPERATIONS
        )
        
        return response.dict()
    
    except Exception as e:
        logger.error(f"Error handling discover request: {e}", exc_info=True)
        error_response = MCPErrorResponse(
            version=MCP_VERSION,
            error="Invalid discover request",
            details={"message": str(e)}
        )
        return error_response.dict()


async def handle_execute(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle an MCP execute request.
    
    Args:
        body: The request body as a dictionary
        
    Returns:
        Execute response as a dictionary
    """
    try:
        request = MCPExecuteRequest(**body)
        request.validate_type()
        
        operation = request.operation
        parameters = request.parameters
        
        try:
            # Execute the requested operation
            result = await execute_operation(operation, parameters)
            
            # Create success response
            response = MCPExecuteResponse(
                version=MCP_VERSION,
                operation=operation,
                result=result
            )
            
            return response.dict()
        
        except ValueError as e:
            # Operation not found or invalid parameters
            logger.error(f"Operation error: {e}")
            error_response = MCPErrorResponse(
                version=MCP_VERSION,
                error="Operation error",
                details={"message": str(e)}
            )
            return error_response.dict()
        
        except Exception as e:
            # Error executing operation
            logger.error(f"Error executing operation {operation}: {e}", exc_info=True)
            error_response = MCPErrorResponse(
                version=MCP_VERSION,
                error="Operation execution failed",
                details={"message": str(e)}
            )
            return error_response.dict()
    
    except Exception as e:
        logger.error(f"Error handling execute request: {e}", exc_info=True)
        error_response = MCPErrorResponse(
            version=MCP_VERSION,
            error="Invalid execute request",
            details={"message": str(e)}
        )
        return error_response.dict()


@app.get("/")
async def root():
    """
    Root endpoint to verify server is running.
    
    Returns:
        Simple response with server information
    """
    return {
        "name": "Geotab MCP Server",
        "version": MCP_VERSION,
        "endpoints": {
            "/mcp": "MCP endpoint for discover and execute operations",
            "/docs": "OpenAPI documentation"
        }
    }
