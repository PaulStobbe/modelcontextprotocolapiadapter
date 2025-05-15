"""
Models for the Model Context Protocol (MCP) implementation.
"""
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field

# MCP version
MCP_VERSION = "0.1.0"

# -------- MCP Request Models --------

class MCPDiscoverRequest(BaseModel):
    """MCP discover request model."""
    type: str = Field(..., description="Request type (must be 'discover')")
    version: str = Field(..., description="MCP version")

    def validate_type(self):
        """Validate that type is 'discover'."""
        if self.type != "discover":
            raise ValueError("Type must be 'discover'")


class MCPExecuteRequest(BaseModel):
    """MCP execute request model."""
    type: str = Field(..., description="Request type (must be 'execute')")
    version: str = Field(..., description="MCP version")
    operation: str = Field(..., description="Operation name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")

    def validate_type(self):
        """Validate that type is 'execute'."""
        if self.type != "execute":
            raise ValueError("Type must be 'execute'")


# -------- MCP Parameter Models --------

class MCPParameter(BaseModel):
    """MCP operation parameter definition."""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, number, boolean, etc.)")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(False, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value if any")


class MCPOperation(BaseModel):
    """MCP operation definition."""
    name: str = Field(..., description="Operation name")
    description: str = Field(..., description="Operation description")
    parameters: List[MCPParameter] = Field(default_factory=list, description="Operation parameters")
    returns: str = Field(..., description="Description of what operation returns")


# -------- MCP Response Models --------

class MCPDiscoverResponse(BaseModel):
    """MCP discover response model."""
    type: str = Field("discover", description="Response type")
    version: str = Field(..., description="MCP version")
    operations: List[MCPOperation] = Field(..., description="Available operations")


class MCPExecuteResponse(BaseModel):
    """MCP execute response model."""
    type: str = Field("execute", description="Response type")
    version: str = Field(..., description="MCP version")
    operation: str = Field(..., description="Executed operation name")
    result: Dict[str, Any] = Field(..., description="Operation result")


class MCPErrorResponse(BaseModel):
    """MCP error response model."""
    type: str = Field("error", description="Response type")
    version: str = Field(..., description="MCP version")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# Union type for all possible MCP responses
MCPResponse = Union[MCPDiscoverResponse, MCPExecuteResponse, MCPErrorResponse]
