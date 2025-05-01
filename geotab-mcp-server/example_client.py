"""Example client that demonstrates using the Geotab MCP Server."""
import json
import argparse
import requests
from typing import Dict, Any, List, Optional


class MCPClient:
    """Client for interacting with MCP servers."""
    
    def __init__(self, server_url: str):
        """Initialize with the MCP server URL."""
        self.server_url = server_url
        self.mcp_version = "0.1.0"
    
    def discover(self) -> Dict[str, Any]:
        """Discover available operations on the MCP server."""
        payload = {
            "type": "discover",
            "version": self.mcp_version
        }
        
        response = requests.post(self.server_url, json=payload)
        return response.json()
    
    def execute(self, operation: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an operation on the MCP server."""
        if parameters is None:
            parameters = {}
            
        payload = {
            "type": "execute",
            "version": self.mcp_version,
            "operation": operation,
            "parameters": parameters
        }
        
        response = requests.post(self.server_url, json=payload)
        return response.json()


def print_operations(operations: List[Dict[str, Any]]):
    """Print available operations in a readable format."""
    print("\nAvailable Operations:")
    print("====================")
    
    for op in operations:
        print(f"\n{op['name']}")
        print("-" * len(op['name']))
        print(f"Description: {op['description']}")
        print(f"Returns: {op['returns']}")
        
        if op['parameters']:
            print("\nParameters:")
            for param in op['parameters']:
                required = "(Required)" if param.get('required', False) else "(Optional)"
                default = f", Default: {param.get('default')}" if param.get('default') is not None else ""
                print(f"  - {param['name']} ({param['type']}) {required}{default}")
                print(f"    {param['description']}")


def print_result(result: Dict[str, Any]):
    """Print operation result in a readable format."""
    print("\nOperation Result:")
    print("================")
    print(json.dumps(result, indent=2))


def main():
    """Main function to run the example client."""
    parser = argparse.ArgumentParser(description="Example client for Geotab MCP Server")
    parser.add_argument("--url", default="http://localhost:8000/mcp", help="MCP server URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Discover command
    discover_parser = subparsers.add_parser("discover", help="Discover available operations")
    
    # Execute commands
    device_info_parser = subparsers.add_parser("get_device_info", help="Get device information")
    device_info_parser.add_argument("--include-inactive", action="store_true", help="Include inactive devices")
    
    device_location_parser = subparsers.add_parser("get_device_location", help="Get device location")
    device_location_parser.add_argument("--device-id", required=True, help="Device ID")
    
    trip_data_parser = subparsers.add_parser("get_trip_data", help="Get trip data")
    trip_data_parser.add_argument("--device-id", required=True, help="Device ID")
    trip_data_parser.add_argument("--days", type=int, default=1, help="Number of days to look back")
    
    fault_data_parser = subparsers.add_parser("get_fault_data", help="Get fault data")
    fault_data_parser.add_argument("--device-id", required=True, help="Device ID")
    fault_data_parser.add_argument("--days", type=int, default=7, help="Number of days to look back")
    fault_data_parser.add_argument("--active-only", action="store_true", help="Show only active faults")
    
    args = parser.parse_args()
    
    # Initialize the client
    client = MCPClient(args.url)
    
    if args.command == "discover" or args.command is None:
        # Discover available operations
        discover_result = client.discover()
        
        if discover_result.get("type") == "error":
            print(f"Error: {discover_result.get('error')}")
            print(f"Details: {discover_result.get('details')}")
            return
            
        operations = discover_result.get("operations", [])
        print_operations(operations)
        
    elif args.command == "get_device_info":
        # Execute get_device_info operation
        parameters = {}
        if args.include_inactive:
            parameters["include_inactive"] = True
            
        result = client.execute("get_device_info", parameters)
        print_result(result)
        
    elif args.command == "get_device_location":
        # Execute get_device_location operation
        parameters = {"device_id": args.device_id}
        result = client.execute("get_device_location", parameters)
        print_result(result)
        
    elif args.command == "get_trip_data":
        # Execute get_trip_data operation
        parameters = {
            "device_id": args.device_id,
            "days": args.days
        }
        result = client.execute("get_trip_data", parameters)
        print_result(result)
        
    elif args.command == "get_fault_data":
        # Execute get_fault_data operation
        parameters = {
            "device_id": args.device_id,
            "days": args.days,
            "active_only": args.active_only
        }
        result = client.execute("get_fault_data", parameters)
        print_result(result)


if __name__ == "__main__":
    main()
