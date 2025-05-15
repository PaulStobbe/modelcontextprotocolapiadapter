"""
Operations for the Geotab MCP server.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .models import MCPParameter, MCPOperation, MCP_VERSION
from geotab.client import GeotabClient

logger = logging.getLogger("mcp.operations")

# Initialize the Geotab client
geotab_client = GeotabClient()

# Define the MCP operations
OPERATIONS = [
    MCPOperation(
        name="get_devices",
        description="Get a list of all devices in the Geotab account",
        parameters=[
            MCPParameter(
                name="include_inactive",
                type="boolean",
                description="Whether to include inactive devices",
                required=False,
                default=False
            )
        ],
        returns="List of devices with their properties and status"
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
        name="get_trips",
        description="Get trip data for a specific device within a time range",
        parameters=[
            MCPParameter(
                name="device_id",
                type="string",
                description="ID of the device to get trips for",
                required=True
            ),
            MCPParameter(
                name="days",
                type="number",
                description="Number of days to look back from current time",
                required=False,
                default=1
            ),
            MCPParameter(
                name="include_stops",
                type="boolean",
                description="Whether to include stop information",
                required=False,
                default=False
            )
        ],
        returns="List of trips with start/end locations, distance, and other metrics"
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
                type="number",
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
        returns="List of fault codes with diagnostic information"
    ),
    MCPOperation(
        name="get_status_data",
        description="Get status data for a device",
        parameters=[
            MCPParameter(
                name="device_id",
                type="string",
                description="ID of the device to get status data for",
                required=True
            ),
            MCPParameter(
                name="diagnostic_id",
                type="string",
                description="ID of the diagnostic to filter by",
                required=False,
                default=None
            ),
            MCPParameter(
                name="hours",
                type="number",
                description="Number of hours to look back from current time",
                required=False,
                default=1
            )
        ],
        returns="List of status data points with timestamp and values"
    )
]

# Map of operation names to their definitions
OPERATION_MAP = {op.name: op for op in OPERATIONS}


# Operation handler implementations

async def handle_get_devices(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get devices implementation.
    
    Args:
        parameters: Operation parameters
        
    Returns:
        Operation result
    """
    include_inactive = parameters.get("include_inactive", False)
    
    # Get devices from Geotab
    devices = geotab_client.get_devices(include_inactive=include_inactive)
    
    return {
        "devices": devices,
        "count": len(devices),
        "timestamp": datetime.now().isoformat()
    }


async def handle_get_device_location(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get device location implementation.
    
    Args:
        parameters: Operation parameters
        
    Returns:
        Operation result
    """
    device_id = parameters.get("device_id")
    if not device_id:
        raise ValueError("device_id is required")
    
    # Get device location from Geotab
    location = geotab_client.get_device_location(device_id=device_id)
    
    if not location:
        return {
            "error": "Location not available for device",
            "device_id": device_id,
            "timestamp": datetime.now().isoformat()
        }
    
    return {
        "location": location,
        "timestamp": datetime.now().isoformat()
    }


async def handle_get_trips(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get trips implementation.
    
    Args:
        parameters: Operation parameters
        
    Returns:
        Operation result
    """
    device_id = parameters.get("device_id")
    if not device_id:
        raise ValueError("device_id is required")
    
    days = float(parameters.get("days", 1))
    include_stops = parameters.get("include_stops", False)
    
    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    
    # Get trips from Geotab
    trips = geotab_client.get_trips(
        device_id=device_id,
        from_date=from_date,
        to_date=to_date,
        include_non_trip_data=include_stops
    )
    
    return {
        "device_id": device_id,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "trips": trips,
        "count": len(trips),
        "timestamp": datetime.now().isoformat()
    }


async def handle_get_fault_data(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get fault data implementation.
    
    Args:
        parameters: Operation parameters
        
    Returns:
        Operation result
    """
    device_id = parameters.get("device_id")
    if not device_id:
        raise ValueError("device_id is required")
    
    days = float(parameters.get("days", 7))
    active_only = parameters.get("active_only", False)
    
    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    
    # Get fault data from Geotab
    faults = geotab_client.get_fault_data(
        device_id=device_id,
        from_date=from_date,
        to_date=to_date,
        include_inactive=not active_only
    )
    
    return {
        "device_id": device_id,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "faults": faults,
        "count": len(faults),
        "timestamp": datetime.now().isoformat()
    }


async def handle_get_status_data(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get status data implementation.
    
    Args:
        parameters: Operation parameters
        
    Returns:
        Operation result
    """
    device_id = parameters.get("device_id")
    if not device_id:
        raise ValueError("device_id is required")
    
    diagnostic_id = parameters.get("diagnostic_id")
    hours = float(parameters.get("hours", 1))
    
    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(hours=hours)
    
    # Get status data from Geotab
    status_data = geotab_client.get_status_data(
        device_id=device_id,
        diagnostic_id=diagnostic_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "device_id": device_id,
        "diagnostic_id": diagnostic_id,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "status_data": status_data,
        "count": len(status_data),
        "timestamp": datetime.now().isoformat()
    }


# Map operation names to their handler functions
OPERATION_HANDLERS = {
    "get_devices": handle_get_devices,
    "get_device_location": handle_get_device_location,
    "get_trips": handle_get_trips,
    "get_fault_data": handle_get_fault_data,
    "get_status_data": handle_get_status_data
}


async def execute_operation(operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an MCP operation.
    
    Args:
        operation: Operation name
        parameters: Operation parameters
        
    Returns:
        Operation result
        
    Raises:
        ValueError: If operation doesn't exist
    """
    if operation not in OPERATION_HANDLERS:
        raise ValueError(f"Unknown operation: {operation}")
    
    logger.info(f"Executing operation {operation} with parameters {parameters}")
    
    try:
        result = await OPERATION_HANDLERS[operation](parameters)
        return result
    except Exception as e:
        logger.error(f"Error executing operation {operation}: {e}", exc_info=True)
        raise
