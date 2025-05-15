#!/usr/bin/env python3
"""
Example client for the Geotab MCP server.
"""
import argparse
import json
import requests

def discover(server_url):
    """
    Send a discover request to get available operations.
    
    Args:
        server_url: URL of the MCP server
        
    Returns:
        Server response as a dictionary
    """
    request = {
        "type": "discover",
        "version": "0.1.0"
    }
    
    response = requests.post(server_url, json=request)
    response.raise_for_status()
    return response.json()

def execute(server_url, operation, parameters):
    """
    Execute an operation on the MCP server.
    
    Args:
        server_url: URL of the MCP server
        operation: Name of the operation to execute
        parameters: Parameters for the operation
        
    Returns:
        Operation result as a dictionary
    """
    request = {
        "type": "execute",
        "version": "0.1.0",
        "operation": operation,
        "parameters": parameters
    }
    
    response = requests.post(server_url, json=request)
    response.raise_for_status()
    return response.json()

def main():
    """
    Main function for the example client.
    """
    parser = argparse.ArgumentParser(description="Geotab MCP Client Example")
    parser.add_argument("--server", default="http://localhost:8000/mcp", help="MCP server URL")
    parser.add_argument("--operation", help="Operation to execute")
    parser.add_argument("--params", help="JSON string with operation parameters")
    args = parser.parse_args()
    
    # If no operation specified, just discover available operations
    if not args.operation:
        print("Discovering available operations...")
        result = discover(args.server)
        
        if result.get("type") == "discover" and "operations" in result:
            operations = result["operations"]
            print(f"\nFound {len(operations)} operations:")
            
            for op in operations:
                print(f"\n- {op['name']}: {op['description']}")
                
                if op['parameters']:
                    print("  Parameters:")
                    for param in op['parameters']:
                        required = "REQUIRED" if param.get("required", False) else "OPTIONAL"
                        default = f", default={param['default']}" if param.get("default") is not None else ""
                        print(f"    - {param['name']} ({param['type']}, {required}{default}): {param['description']}")
                else:
                    print("  No parameters required.")
                
                print(f"  Returns: {op['returns']}")
        else:
            print(f"Error in discover response: {result}")
    
    # Execute the specified operation
    else:
        parameters = {}
        if args.params:
            try:
                parameters = json.loads(args.params)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in parameters: {args.params}")
                return
        
        print(f"Executing operation '{args.operation}' with parameters: {parameters}")
        result = execute(args.server, args.operation, parameters)
        
        if result.get("type") == "execute" and "result" in result:
            print("\nOperation result:")
            print(json.dumps(result["result"], indent=2))
        else:
            print(f"Error in execute response: {result}")

if __name__ == "__main__":
    main()
