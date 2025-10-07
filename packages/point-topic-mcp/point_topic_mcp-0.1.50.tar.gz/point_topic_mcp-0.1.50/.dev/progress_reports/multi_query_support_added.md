# multi-query support added to execute_query tool

## changes made

**snowflake connector (`snowflake.py`)**:
- added `execute_safe_queries()` method that handles multiple queries separated by semicolons
- splits queries, validates each individually, executes separately
- returns clearly labeled results with query numbers and separators

**mcp tool (`mcp_tools.py`)**:
- updated `execute_query()` to use new multi-query method
- enhanced docstring with examples of single/multiple query usage
- maintains backward compatibility - single queries work exactly as before

## format for multiple queries
```
=== QUERY 1 ===
SQL: select count(*) from table1
RESULTS:
count
42

=== QUERY 2 ===  
SQL: select avg(price) from table2
RESULTS:
avg_price
15.50
```

## agent benefits
- can now execute related queries in one tool call: `"SELECT ...; SELECT ...; SHOW ..."`
- clear separation of results prevents confusion
- reduces back-and-forth, improves efficiency
- maintains all existing safety validations per query

## backward compatibility
- single queries work exactly as before
- no breaking changes to existing functionality
- seamless upgrade for agents and users
