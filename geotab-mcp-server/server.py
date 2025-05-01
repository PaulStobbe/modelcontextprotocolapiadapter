"""Main entry point for the Geotab MCP Server."""
import os
import logging
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("main")

def main():
    """Start the MCP server."""
    # Get server configuration from environment
    host = os.environ.get("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_SERVER_PORT", 8000))
    
    logger.info(f"Starting Geotab MCP Server on {host}:{port}")
    
    # Start the server
    uvicorn.run(
        "mcp_server.server:app", 
        host=host, 
        port=port,
        reload=True
    )

if __name__ == "__main__":
    main()
