"""MCP operations for Geotab APIs."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from geotab_api.client import GeotabClient

class GeotabOperations:
    """MCP operations implementation for Geotab APIs."""

    def __init__(self):
        """Initialize with a Geotab client."""
        self.client = GeotabClient()

    async def get_device_info(self, include_inactive: bool = False) -> Dict[str, Any]:
        """
        Get information about all devices.
        
        Args:
            include_inactive: Whether to include inactive devices in the results.
            
        Returns:
            A dictionary with device information.
        """
        devices = self.client.get_devices()
        
        if not include_inactive:
            devices = [device for device in devices if device.get('active', True)]
            
        return {
            "operation": "get_device_info",
            "result": {
                "devices": devices,
                "count": len(devices),
                "timestamp": datetime.now().isoformat()
            }
        }

    async def get_device_location(self, device_id: str) -> Dict[str, Any]:
        """
        Get the current location of a specific device.
        
        Args:
            device_id: The ID of the device.
            
        Returns:
            A dictionary with the device's location information.
        """
        location = self.client.get_device_location(device_id)
        
        if not location:
            return {
                "operation": "get_device_location",
                "result": {
                    "error": "Device location not found",
                    "device_id": device_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        return {
            "operation": "get_device_location",
            "result": {
                "location": location,
                "timestamp": datetime.now().isoformat()
            }
        }

    async def get_trip_data(self, 
                           device_id: str, 
                           days: int = 1) -> Dict[str, Any]:
        """
        Get trip data for a specific device within a time range.
        
        Args:
            device_id: The ID of the device.
            days: Number of days to look back (default: 1).
            
        Returns:
            A dictionary with trip data.
        """
        from_date = datetime.now() - timedelta(days=days)
        to_date = datetime.now()
        
        trips = self.client.get_trip_data(
            device_id=device_id,
            from_date=from_date,
            to_date=to_date
        )
        
        return {
            "operation": "get_trip_data",
            "result": {
                "device_id": device_id,
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat(),
                "trips": trips,
                "count": len(trips),
                "timestamp": datetime.now().isoformat()
            }
        }

    async def get_fault_data(self, 
                            device_id: str, 
                            days: int = 7, 
                            active_only: bool = False) -> Dict[str, Any]:
        """
        Get fault codes and diagnostic data for a device.
        
        Args:
            device_id: The ID of the device.
            days: Number of days to look back (default: 7).
            active_only: Whether to include only active faults.
            
        Returns:
            A dictionary with fault data.
        """
        from_date = datetime.now() - timedelta(days=days)
        to_date = datetime.now()
        
        faults = self.client.get_fault_data(
            device_id=device_id,
            from_date=from_date,
            to_date=to_date
        )
        
        if active_only:
            faults = [fault for fault in faults if fault.get('active', False)]
        
        return {
            "operation": "get_fault_data",
            "result": {
                "device_id": device_id,
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat(),
                "faults": faults,
                "count": len(faults),
                "active_only": active_only,
                "timestamp": datetime.now().isoformat()
            }
        }

    # MCP operation mapping
    operation_map = {
        "get_device_info": get_device_info,
        "get_device_location": get_device_location,
        "get_trip_data": get_trip_data,
        "get_fault_data": get_fault_data
    }
