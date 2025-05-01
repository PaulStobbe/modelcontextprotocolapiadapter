"""Pydantic models for MCP server."""
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field


class MCPDiscoverRequest(BaseModel):
    """Model for MCP discover request."""
    type: str = Field("discover", const=True)
    version: str = Field(..., description="The MCP version to use")


class MCPParameter(BaseModel):
    """Model for an MCP operation parameter."""
    name: str = Field(..., description="The name of the parameter")
    type: str = Field(..., description="The parameter type")
    description: str = Field(..., description="Description of the parameter")
    required: bool = Field(False, description="Whether the parameter is required")
    default: Optional[Any] = Field(None, description="The default value if any")


class MCPOperation(BaseModel):
    """Model for an MCP operation definition."""
    name: str = Field(..., description="The name of the operation")
    description: str = Field(..., description="Description of the operation")
    parameters: List[MCPParameter] = Field(default_factory=list, description="Parameters of the operation")
    returns: str = Field(..., description="Description of what the operation returns")


class MCPDiscoverResponse(BaseModel):
    """Model for MCP discover response."""
    type: str = Field("discover", const=True)
    version: str = Field(..., description="The MCP version in use")
    operations: List[MCPOperation] = Field(..., description="Available operations")


class MCPExecuteRequest(BaseModel):
    """Model for MCP execute request."""
    type: str = Field("execute", const=True)
    version: str = Field(..., description="The MCP version to use")
    operation: str = Field(..., description="The operation to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the operation")


class MCPExecuteResponse(BaseModel):
    """Model for MCP execute response."""
    type: str = Field("execute", const=True)
    version: str = Field(..., description="The MCP version in use")
    operation: str = Field(..., description="The executed operation")
    result: Dict[str, Any] = Field(..., description="The operation result")


class MCPErrorResponse(BaseModel):
    """Model for MCP error response."""
    type: str = Field("error", const=True)
    version: str = Field(..., description="The MCP version in use")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


MCPResponse = Union[MCPDiscoverResponse, MCPExecuteResponse, MCPErrorResponse]
