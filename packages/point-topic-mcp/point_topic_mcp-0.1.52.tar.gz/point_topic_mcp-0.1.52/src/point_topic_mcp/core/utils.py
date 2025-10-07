from typing import Callable, List, Tuple, Any
from functools import wraps
import os




# DECORATORS

# Store tool requirements for status reporting
_TOOL_REQUIREMENTS = {}

def check_env_vars(tool_name: str, env_vars: List[str]) -> bool:
    """
    Check if environment variables are available and track for status reporting.
    
    Args:
        tool_name: Name of the tool for tracking
        env_vars: List of environment variable names that must be set
        
    Returns:
        bool: True if all environment variables are present
    """
    # Store tool requirements for status reporting
    all_present = all(os.getenv(var) for var in env_vars)
    _TOOL_REQUIREMENTS[tool_name] = {
        'env_vars': env_vars,
        'available': all_present
    }
    
    if not all_present:
        missing_vars = [var for var in env_vars if not os.getenv(var)]
        print(f"[MCP] Skipping {tool_name}: missing env vars {missing_vars}")
    else:
        print(f"[MCP] Registering {tool_name}: env vars {env_vars} ✓")
    
    return all_present


def get_mcp_status_info() -> str:
    """Generate status information about available and missing tools."""
    if not _TOOL_REQUIREMENTS:
        return "All tools available (no conditional tools detected)"
    
    available_tools = []
    missing_tools = []
    
    for tool_name, info in _TOOL_REQUIREMENTS.items():
        if info['available']:
            available_tools.append(tool_name)
        else:
            missing_env_vars = [var for var in info['env_vars'] if not os.getenv(var)]
            missing_tools.append(f"{tool_name} (needs: {', '.join(missing_env_vars)})")
    
    status_parts = []
    
    if available_tools:
        status_parts.append(f"✓ Available: {len(available_tools)} conditional tools")
    
    if missing_tools:
        status_parts.append(f"✗ Missing: {len(missing_tools)} tools need env vars")
        status_parts.append("Missing tools: " + " | ".join(missing_tools))
    
    if not missing_tools:
        status_parts.append("All conditional tools available!")
    
    return " | ".join(status_parts)


def dynamic_docstring(replacements: List[Tuple[str, Callable[[], str]]]):
    """
    Decorator to dynamically replace placeholders in docstrings.
    
    Args:
        replacements: List of [placeholder, function] pairs
                     where placeholder is replaced with function's return value
    
    Example:
        @dynamic_docstring([("{DATASETS}", list_datasets)])
        def my_tool():
            '''Tool with {DATASETS} placeholder'''
            pass
    """
    def decorator(func):
        # Get original docstring
        original_doc = func.__doc__ or ""
        
        # Apply all replacements
        updated_doc = original_doc
        for placeholder, replacement_func in replacements:
            try:
                replacement_value = replacement_func()
                updated_doc = updated_doc.replace(placeholder, replacement_value)
            except Exception as e:
                print(f"Warning: Failed to replace {placeholder} in {func.__name__}: {e}")
                # Keep placeholder if replacement fails
        
        # Update the docstring
        func.__doc__ = updated_doc
        
        return func
    
    return decorator
