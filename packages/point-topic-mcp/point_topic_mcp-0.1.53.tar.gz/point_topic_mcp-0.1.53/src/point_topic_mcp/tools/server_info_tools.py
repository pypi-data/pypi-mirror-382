"""Server information and capability tools."""

from typing import Optional
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from point_topic_mcp.core.utils import dynamic_docstring, get_mcp_status_info

@dynamic_docstring([("{STATUS}", get_mcp_status_info)])
def get_mcp_server_capabilities(ctx: Optional[Context[ServerSession, None]] = None) -> str:
    """MCP Server Configuration Status and Available Tools
    
    Shows which tools are available and which need environment variables.
    Use this to debug missing tools or check your MCP server configuration.
    
    Current Status: {STATUS}
    
    Environment Variables Guide:
    • SNOWFLAKE_USER + SNOWFLAKE_PASSWORD → Database tools (execute_query, assemble_dataset_context, etc.)
    • CHART_API_KEY → Authenticated chart generation (generate_authenticated_chart_url)
    • Public chart tools available without credentials (get_point_topic_public_chart_catalog)
    
    Configure missing environment variables in your MCP client to unlock additional tools.
    """
    return get_mcp_status_info()
