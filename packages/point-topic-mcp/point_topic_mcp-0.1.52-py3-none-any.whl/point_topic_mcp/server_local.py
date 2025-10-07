"""Local MCP server using stdio transport for Claude Desktop integration."""

import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from point_topic_mcp.tools import register_tools

# Create FastMCP instance (at module level)
mcp = FastMCP(
    name="Point Topic MCP",
    instructions="UK broadband data analysis server for local development"
)

def main():
    """Main entry point for the MCP server."""
    # Load environment variables (happens when server actually starts)
    load_dotenv()
    
    # Register tools after environment is ready
    register_tools(mcp)
    
    # Run with stdio transport (default for local/Claude Desktop)
    mcp.run()

if __name__ == "__main__":
    main()
