"""
Main entrypoint for the Geotab MCP server.
"""
import os
import logging
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/mcp_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

def main():
    """Start the MCP server."""
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))
    
    logger.info(f"Starting Geotab MCP Server on {host}:{port}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Start the server
    uvicorn.run(
        "mcp.server:app", 
        host=host, 
        port=port
    )

if __name__ == "__main__":
    main()
