"""MCP tools module with auto-discovery and registration."""

import importlib
import pkgutil
import inspect
from pathlib import Path


def register_tools(mcp):
    """Register all MCP tools by auto-discovering functions in tool modules.
    
    Automatically finds all Python modules in the tools directory and registers
    every public function (not starting with _) as an MCP tool.
    
    Just create a .py file with tool functions - no wrapper functions or decorators needed!
    """
    # Get the tools package directory
    tools_dir = Path(__file__).parent
    
    # Discover all Python modules in this directory
    for module_info in pkgutil.iter_modules([str(tools_dir)]):
        # Skip __init__ and any private modules
        if module_info.name.startswith('_'):
            continue
        
        try:
            # Import the module
            module = importlib.import_module(f'.{module_info.name}', package='point_topic_mcp.tools')
            
            # Find all functions defined in this module (not imported from elsewhere)
            tool_count = 0
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                # Skip private functions
                if name.startswith('_'):
                    continue
                
                # Only register functions actually defined in this module (not imported)
                if obj.__module__ == module.__name__:
                    mcp.tool()(obj)
                    tool_count += 1
            
            if tool_count > 0:
                print(f"[MCP] Registered {tool_count} tools from {module_info.name}")
        
        except Exception as e:
            print(f"[MCP] Warning: Failed to load tools from {module_info.name}: {e}")
            import traceback
            traceback.print_exc()
            # Continue with other modules even if one fails


__all__ = ["register_tools"]
