import snowflake.connector
from dotenv import load_dotenv
import os
import re

class SnowflakeDB:
    """
    Class for connecting to the Snowflake database.
    
    Example usage:
        `db = SnowflakeDB()`
        `db.connect()`
        `result = db.execute_safe_query(sql_query)`
        `db.close_connection()`

    Attributes:
        user (str): Snowflake user.
        password (str): Snowflake password.
        account (str): Snowflake account.
        warehouse (str): Snowflake warehouse.
        database (str): Snowflake database.
        schema (str): Snowflake schema.
        connection (snowflake.connector.connection.SnowflakeConnection): Snowflake connection.
    """
    def __init__(self):
        # Load environment variables only when needed
        try:
            load_dotenv()
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")
        
        # credentials loaded from environment variables

        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        
        self.account = 'fz24086.eu-west-1'
        self.warehouse = 'COMPUTE_WH'
        self.database = 'UPC_CORE'
        self.schema = 'REPORTS'

        self.connection = None

    def connect(self):
        """Establishes a connection to the Snowflake database."""
        self.connection = snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema
        )

    def close_connection(self):
        """Closes the Snowflake database connection."""
        if self.connection is not None:
            self.connection.close()

    def query_to_df(self, query):
        """Executes a given SQL query and returns the results as a Pandas DataFrame."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            df = cursor.fetch_pandas_all()
            return df
        finally:
            cursor.close()

    def query_to_json(self, query):
        """Executes a given SQL query and returns the results as a JSON string."""
        df = self.query_to_df(query)
        return df.to_json(orient='records')

    def query_to_csv(self, query):
        """Executes a given SQL query and returns the results as a CSV string."""
        df = self.query_to_df(query)
        return df.to_csv(index=False)

    def execute_ddl(self, query):
        """Executes a DDL statement such as CREATE or ALTER and returns True if successful."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return True
        finally:
            cursor.close()

    def get_distinct_value_list(self, table, column):
        """Gets the distinct list of values for a given column in a given table."""
        query = f"select distinct {column} from {table}"
        return self.query_to_csv(query)

    def validate_safe_query(self, query: str) -> tuple[bool, str]:
        """
        Validates that a SQL query is safe to execute (read-only operations only).
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Remove comments and normalize whitespace
        clean_query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
        clean_query = clean_query.strip().upper()
        
        # Dangerous keywords that should never be allowed
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 
            'TRUNCATE', 'REPLACE', 'MERGE', 'COPY', 'PUT', 'GET',
            'REMOVE', 'GRANT', 'REVOKE', 'USE', 'SET', 'UNSET',
            'CALL', 'EXECUTE', 'EXEC'
        ]
        
        # Check for dangerous keywords at word boundaries
        for keyword in dangerous_keywords:
            if re.search(rf'\b{keyword}\b', clean_query):
                return False, f"Query contains prohibited keyword: {keyword}"
        
        # Must start with SELECT, WITH, SHOW, DESCRIBE, or EXPLAIN
        allowed_start_keywords = ['SELECT', 'WITH', 'SHOW', 'DESCRIBE', 'DESC', 'EXPLAIN']
        
        starts_with_allowed = any(clean_query.startswith(keyword) for keyword in allowed_start_keywords)
        if not starts_with_allowed:
            return False, f"Query must start with one of: {', '.join(allowed_start_keywords)}"
        
        # Additional safety checks
        if ';' in query[:-1]:  # Semicolon not at the end (potential SQL injection)
            return False, "Multiple statements not allowed"
            
        return True, ""

    def execute_safe_query(self, query: str) -> str:
        """
        Executes a validated safe SQL query and returns results as CSV.
        Handles all validation and errors internally.
        
        Args:
            query: SQL query to execute (must be read-only)
            
        Returns:
            str: Query results as CSV format or error message
        """
        # Validate query safety
        is_valid, error_message = self.validate_safe_query(query)
        if not is_valid:
            return f"ERROR: Query validation failed - {error_message}"
        
        # Execute query with error handling
        try:
            return self.query_to_csv(query)
        except Exception as e:
            return f"DATABASE ERROR: {str(e)}"
    
    def execute_safe_queries(self, queries: str) -> str:
        """
        Executes multiple validated safe SQL queries separated by semicolons.
        Each query is validated and executed separately.
        
        Args:
            queries: Multiple SQL queries separated by semicolons (must be read-only)
            
        Returns:
            str: Combined results with clear query separators
        """
        # Split queries by semicolon and clean them
        query_list = [q.strip() for q in queries.split(';') if q.strip()]
        
        if len(query_list) == 1:
            # Single query, use the regular method
            return self.execute_safe_query(query_list[0])
        
        results = []
        for i, query in enumerate(query_list, 1):
            results.append(f"=== QUERY {i} ===")
            results.append(f"SQL: {query}")
            results.append("RESULTS:")
            
            # Execute each query individually
            result = self.execute_safe_query(query)
            results.append(result)
            results.append("")  # Empty line for separation
        
        return "\n".join(results)

    def describe_table(self, table_name: str) -> str:
        """
        Describe a table in the Snowflake database.

        Args:
            table_name: The name of the table to describe. 
            Use the full database and schema name.
            e.g. "upc_core.reports.upc_output"

        Returns:
            The schema as CSV string
        """
        query = f"describe table {table_name}"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            import io
            output = io.StringIO()
            output.write(','.join(columns) + '\n')
            for row in rows:
                output.write(','.join(str(cell) if cell is not None else '' for cell in row) + '\n')
            return output.getvalue()
        finally:
            cursor.close()