# MCP Server Snowflake Integration Troubleshooting Report

## Problem

MCP server disconnects when importing Snowflake connector, even though the code works when run directly.

## Root Cause

Environment variable `VIRTUAL_ENV` was set to old weather project (`/Users/peterdonaghey/Projects/weather/.venv`), causing uv to use wrong virtual environment.

## Attempts Made

### 1. Lazy Import Pattern (Updated)

- **Approach**: Import snowflake only when needed (moved import inside connect() method)
- **Result**: Server starts without hanging, but hides actual errors when tool is called
- **Problem**: Makes debugging impossible - Claude can see errors but user can't
- **Status**: ❌ Removed - hiding real errors is worse than startup issues

### 2. Environment Variable Fix

- **Approach**: Clear `VIRTUAL_ENV` variable before running commands
- **Command**: `unset VIRTUAL_ENV && uv run mcp install src/server.py`
- **Result**: Fixed environment detection
- **Status**: ✅ Partial success

### 3. Import Path Issues

- **Problem**: `ModuleNotFoundError: No module named 'src'`
- **Attempted**: Absolute imports (`from src.db.snowflake_connector import SnowflakeDB`)
- **Result**: Failed when running from project root
- **Status**: ❌ Failed

### 4. Relative Imports

- **Approach**: Use relative imports (`from db.snowflake_connector import SnowflakeDB`)
- **Requirement**: Must run from `src/` directory
- **Result**: Works when tested directly
- **Status**: ✅ Works in isolation

### 5. Python Path Manipulation

- **Approach**: Add project root to sys.path
- **Code**: `sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`
- **Result**: User rejected - already tried this approach
- **Status**: ❌ Rejected

## Current State

- ✅ **ROOT CAUSE IDENTIFIED**: MCP server runs in temporary uv environment without snowflake package
- Files moved to top level - confirms import paths are not the issue
- Server starts successfully but snowflake module unavailable at runtime
- Need to ensure snowflake-connector-python is available in MCP's runtime environment

### 6. Direct Testing Results

- **Test**: Called `get_distinct_operator_list()` directly from `src/` directory
- **Result**: ✅ Works perfectly - returns operator data successfully
- **Conclusion**: The snowflake connector itself is fine
- **Problem**: MCP client likely running server from wrong directory

## Next Steps

1. ✅ **SOLUTION IDENTIFIED**: MCP client running server from wrong directory
2. Created wrapper script `run_server.py` to ensure correct working directory
3. Update MCP client config to use wrapper script instead of `src/server.py`
4. Alternative: Move `server.py` to project root and fix imports

## Proposed Fix

Created `run_server.py` wrapper that:

- Changes working directory to `src/`
- Adds `src/` to Python path
- Imports and runs the server with correct environment

### 7. Debugging Environment Differences ✅ SOLUTION FOUND

- **Approach**: Added debug logging to `get_distinct_operator_list()` tool
- **Purpose**: Compare environment when called through Claude vs direct execution
- **Debug Info**: Python path, working dir, virtual env, snowflake availability
- **Status**: ✅ **ROOT CAUSE IDENTIFIED**

**DEBUG OUTPUT FROM CLAUDE**:

- Python path: `/Users/peterdonaghey/.cache/uv/builds-v0/.tmpSso1S7/bin/python`
- Working directory: `/`
- Virtual environment: `/Users/peterdonaghey/.cache/uv/builds-v0/.tmpSso1S7`
- snowflake_available: `False`
- Error: `"No module named 'snowflake'"`

**ROOT CAUSE**: MCP server runs in a temporary uv environment that doesn't have snowflake-connector-python installed, despite it being in pyproject.toml

### 8. File Structure Simplification

- **Approach**: Moved all files to top level to eliminate any import path issues
- **Files moved**: `src/server.py` → `server.py`, `src/db/snowflake_connector.py` → `snowflake_connector.py`
- **Result**: Confirms issue is NOT import paths - it's missing snowflake package in MCP environment
- **Status**: ✅ Import issues definitively ruled out

## Key Learnings

- Environment variable pollution from previous projects can break uv
- ~~MCP servers are sensitive to import timing and side effects~~ ❌ WRONG - it's environment isolation
- ~~Relative vs absolute imports behave differently in MCP context~~ ❌ WRONG - relative imports work fine
- ~~Snowflake connector may have initialization code that interferes with MCP stdio communication~~ ❌ WRONG - it's missing entirely
- **CRITICAL**: MCP servers run in isolated uv environments that may not include all dependencies from pyproject.toml
- **CRITICAL**: MCP install requires explicit `--with` flag to include additional dependencies
- Debug logging is essential - assumptions about environment are often wrong
- pyproject.toml dependencies are NOT automatically available in MCP runtime environments

### 9. SOLUTION FOUND ✅

- **Discovery**: MCP install command requires explicit dependency declaration with `--with` flag
- **Working Command**: `uv run mcp install server.py --with "snowflake-connector-python[pandas]"`
- **Root Issue**: MCP doesn't automatically include all pyproject.toml dependencies in its runtime environment
- **Status**: ✅ **SOLVED**

**Why this works**:

- MCP creates isolated temporary environments for servers
- Dependencies in pyproject.toml are NOT automatically included
- The `--with` flag explicitly adds required packages to the MCP runtime environment
- This ensures snowflake-connector-python is available when Claude calls the tools

## Final Solution

### The Proper Way (Should Work)

```bash
uv run mcp install server.py
```

**Key insight**: When `mcp[cli]` is included in `pyproject.toml` dependencies (which it is), using `uv run mcp install` should automatically use the project environment with all dependencies.

### The Workaround (If needed)

```bash
uv run mcp install server.py --with "snowflake-connector-python[pandas]"
```

**Why the workaround was needed**: MCP was creating isolated environments instead of using the project environment. This appears to be a design issue where MCP doesn't properly respect `pyproject.toml` dependencies.

**Documentation Gap**: The [official MCP Python SDK docs](https://github.com/modelcontextprotocol/python-sdk) don't mention the `--with` flag requirement, suggesting this behavior is unintended.
