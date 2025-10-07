# Point Topic MCP Server

UK broadband data analysis server via Model Context Protocol. Simple stdio-based server for local development and Claude Desktop integration.

## ✅ what's implemented

**database tools** (requires Snowflake credentials):
- `assemble_dataset_context()` - get schemas and examples for datasets (upc, upc_take_up, upc_forecast, tariffs, ontology)
- `execute_query()` - run safe read-only SQL queries
- `describe_table()` - get table schema details
- `get_la_code()` / `get_la_list_full()` - local authority lookups

**chart tools**:
- `get_point_topic_public_chart_catalog()` - browse public charts (no auth needed)
- `get_point_topic_public_chart_csv()` - get public chart data as CSV (no auth needed)
- `get_point_topic_chart_catalog()` - get complete catalog including private charts (requires API key)
- `get_point_topic_chart_csv()` - get any chart data as CSV with authentication (requires API key)
- `generate_authenticated_chart_url()` - create signed URLs for private charts (requires API key)

**server info**:
- `get_mcp_server_capabilities()` - check which tools are available and debug missing credentials

**conditional availability**: tools only appear if required environment variables are set

## installation (for end users)

**simple pip install**:

```bash
pip install point-topic-mcp
```

**add to your MCP client** (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "point-topic": {
      "command": "point-topic-mcp",
      "env": {
        "SNOWFLAKE_USER": "your_user", 
        "SNOWFLAKE_PASSWORD": "your_password",
        "CHART_API_KEY": "your_chart_api_key"
      }
    }
  }
}
```

**note**: environment variables are optional - tools will only appear if credentials are provided. use `get_mcp_server_capabilities()` to check which tools are available.

**Claude Desktop config location**:
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## development setup

setup: `uv sync`

**for local development with claude desktop**:

This will add the server to your claude desktop config.

```bash
uv run mcp install src/point_topic_mcp/server_local.py --with "snowflake-connector-python[pandas]" -f .env
```

**for mcp inspector**:

```bash
uv run mcp dev src/point_topic_mcp/server_local.py
```

**environment configuration**:

create `.env` file with your credentials:

```bash
# Snowflake database credentials (for database tools)
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password

# Chart API key (for authenticated chart generation)
CHART_API_KEY=your_chart_api_key
```

## architecture

**stdio transport**: communicates with MCP clients via standard input/output for local integration

**auto-discovery**: tools and datasets are automatically discovered from module files - no manual registration needed

**conditional tools**: tools only register if required environment variables are present - use `get_mcp_server_capabilities()` to debug

**modular design**:
- `src/point_topic_mcp/tools/` - tool modules auto-discovered and registered
- `src/point_topic_mcp/context/datasets/` - dataset modules auto-discovered for context assembly

## adding new tools

this project uses auto-discovery for tools - just add a function and it becomes available.

### tool structure

create a file in `src/point_topic_mcp/tools/` ending with `_tools.py`:

```python
# src/point_topic_mcp/tools/my_feature_tools.py

from typing import Optional
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

def my_new_tool(param: str, ctx: Optional[Context[ServerSession, None]] = None) -> str:
    """Tool description visible to agents."""
    # your implementation
    return "result"
```

**that's it!** the tool is automatically discovered and registered.

### conditional tools (require credentials)

use `check_env_vars()` to conditionally define tools:

```python
from point_topic_mcp.core.utils import check_env_vars
from dotenv import load_dotenv

load_dotenv()

if check_env_vars('my_feature', ['MY_API_KEY']):
    def authenticated_tool(ctx: Optional[Context[ServerSession, None]] = None) -> str:
        """Only available if MY_API_KEY is set."""
        import os
        api_key = os.getenv('MY_API_KEY')
        # use api_key...
        return "result"
```

### key principles

1. **auto-discovery**: any public function in `*_tools.py` files becomes a tool
2. **conditional registration**: wrap in `if check_env_vars()` for authenticated tools
3. **clear docstrings**: visible to agents at all times - keep concise and actionable
4. **type hints**: use for better agent understanding

## adding new datasets

this project uses a modular dataset system that allows easy addition of new data sources. each dataset is self-contained and automatically discovered by the MCP server.

### dataset structure

each dataset is a python module in `src/point_topic_mcp/context/datasets/` with two required functions:

```python
def get_dataset_summary():
    """Brief description visible to agents at all times.
    Keep concise - this goes in every agent prompt."""
    return "short description of what data is available"

def get_db_info():
    """Complete context: schema, instructions, examples.
    Only loaded when agent requests this dataset."""
    return f"""
    {DB_INFO}
    
    {DB_SCHEMA}
    
    {SQL_EXAMPLES}
    """
```

### key principles

1. **context window efficiency**: keep `get_dataset_summary()` extremely concise - it's always visible to agents
2. **lazy loading**: full context via `get_db_info()` only loads when needed
3. **self-contained**: each dataset module includes all its own schema, examples, and usage notes
4. **auto-discovery**: new `.py` files in the datasets directory are automatically available

### adding a new dataset

1. **create the module**: `src/point_topic_mcp/context/datasets/your_dataset.py`
2. **implement required functions**: `get_dataset_summary()` and `get_db_info()`
3. **test locally**: `uv run mcp dev src/point_topic_mcp/server_local.py`
4. **verify discovery**: agent should see your dataset in `assemble_dataset_context()` tool description

see existing modules (`upc.py`, `upc_take_up.py`, `upc_forecast.py`) for structure examples.

### optimization tips

- prioritize essential info in summaries
- use clear table descriptions that help agents choose the right dataset
- include common query patterns in examples
- sanity check data against known UK facts in instructions

## publishing to PyPI (for maintainers)

**build and test locally**:

```bash
# Build the package with UV (super fast!)
uv build

# Test installation locally
pip install dist/point_topic_mcp-*.whl

# Test the command works
point-topic-mcp
```

**publish to PyPI**:

```bash
# Set up PyPI credentials in ~/.pypirc first (one time setup)
# [pypi]
#   username = __token__
#   password = pypi-xxxxx...

# Publish to PyPI with the publish script
./publish_to_pypi.sh
```

**test installation from PyPI**:

```bash
pip install point-topic-mcp
point-topic-mcp
```