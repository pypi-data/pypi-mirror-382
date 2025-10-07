"""Snowflake database query and analysis tools."""

from typing import List, Optional
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
from point_topic_mcp.core.context_assembly import list_datasets, assemble_context
from point_topic_mcp.core.utils import dynamic_docstring, check_env_vars
from dotenv import load_dotenv

load_dotenv()

# Snowflake database tools (require credentials)
if check_env_vars('snowflake_tools', ['SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD']):
    @dynamic_docstring([("{DATASETS}", list_datasets)])
    def assemble_dataset_context(
        dataset_names: List[str], 
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """
        Assemble full context (instructions, schema, examples) for one or more datasets.

        This is essential before executing a query, for the agent to understand how to query the datasets.
        
        Args:
            dataset_names: List of dataset names to include (e.g., ['upc', 'upc_take_up'])
        
        {DATASETS}
        
        Returns the complete context needed for querying these datasets.
        """
        return assemble_context(dataset_names)

    def execute_query(
        sql_query: str, 
        ctx: Optional[Context[ServerSession, None]] = None
    ) -> str:
        """
        Execute safe SQL queries against the Snowflake database.
        Only read-only queries allowed (SELECT, WITH, SHOW, DESCRIBE, EXPLAIN).
        
        Multiple queries can be executed in one call by separating them with semicolons (;).
        Each query will be validated and executed separately, with clearly labeled results.
        
        You must first assemble the context for the datasets you are querying using the assemble_dataset_context tool.

        Args:
            sql_query: The SQL query or queries to execute (separated by semicolons for multiple queries)
            
        Returns:
            Query results in CSV format or error message.
            For multiple queries, results are clearly separated with query labels.
            
        Examples:
            Single query: "SELECT COUNT(*) FROM table1"
            Multiple queries: "SELECT COUNT(*) FROM table1; SELECT AVG(price) FROM table2; SHOW TABLES"
        """
        from point_topic_mcp.connectors.snowflake import SnowflakeDB

        sf = SnowflakeDB()
        sf.connect()
        
        # Use the new multi-query method that handles both single and multiple queries
        result = sf.execute_safe_queries(sql_query)
        
        sf.close_connection()
        return result

    def describe_table(table_name: str, ctx: Optional[Context[ServerSession, None]] = None) -> str:
        """
        Describe a table in the Snowflake database.

        Note the schema is already included in the assemble context function

        Args:
            table_name: The name of the table to describe. 
            Use the full database and schema name.
            e.g. "upc_core.reports.upc_output"

        Returns:
            The schema as CSV string
        """
        from point_topic_mcp.connectors.snowflake import SnowflakeDB
        sf = SnowflakeDB()
        sf.connect()
        result = sf.describe_table(table_name)
        sf.close_connection()
        return result

    def get_la_code(la_name: str, ctx: Optional[Context[ServerSession, None]] = None) -> str:
        """
        Get the LA code for a given LA name.

        Args:
            la_name: The name of the LA to get the code for

        Returns:
            The LA code for the given LA name

        Example:
            get_la_code("Westminster") -> "E09000033"
        """
        from point_topic_mcp.connectors.snowflake import SnowflakeDB

        sql_query = f"select distinct la_code from upc_core.reports.upc_output where lower(la_name) like lower('{la_name}')"
        sf = SnowflakeDB()
        sf.connect()
        result = sf.execute_safe_query(sql_query)
        sf.close_connection()
        return result

    def get_la_list_full(la_name: str, ctx: Optional[Context[ServerSession, None]] = None) -> str:
        """
        Get the full list of LA codes and names.

        Can be used if the get_la_code tool doesn't match the LA name.

        Returns the full list of LA codes and names in CSV format.
        """
        from point_topic_mcp.connectors.snowflake import SnowflakeDB

        sql_query = f"select distinct la_code, la_name from upc_core.reports.upc_output"
        sf = SnowflakeDB()
        sf.connect()
        result = sf.execute_safe_query(sql_query)
        sf.close_connection()
        return result
