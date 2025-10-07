# dataset addition prompt template

use this template when adding a new dataset to the point topic mcp server.

## prompt for agent

```
i need to add a new dataset called "{DATASET_NAME}" to the point topic mcp server.

**database context**:
- database/schema: {DATABASE_SCHEMA_NAME}
- main tables: {LIST_OF_MAIN_TABLES}
- data description: {BRIEF_DESCRIPTION_OF_DATA}

**requirements**:
1. create `src/point_topic_mcp/context/datasets/{dataset_name}.py`
2. implement `get_dataset_summary()` - keep extremely concise (visible to agents always)
3. implement `get_db_info()` with:
   - DB_INFO: key concepts, naming conventions, critical usage notes
   - DB_SCHEMA: table schemas with column comments
   - **SQL_EXAMPLES: 3-5 realistic query examples with requests/responses (REQUIRED)**

**context window optimization**:
- prioritize essential info only
- condense verbose descriptions
- focus on what agents need to query successfully
- include common mistake prevention

**follow the pattern from existing datasets** (upc.py, upc_take_up.py, upc_forecast.py)

**test after creation**:
`uv run mcp dev src/point_topic_mcp/server_local.py`

the dataset should auto-appear in assemble_dataset_context() tool.
```

## example usage

```
i need to add a new dataset called "tariffs" to the point topic mcp server.

**database context**:
- database/schema: tariff_core.reports
- main tables: tariff_plans, tariff_pricing, tariff_features
- data description: uk broadband service pricing and plan details by isp

**requirements**:
[...rest of template...]
```

## key principles for dataset modules

### get_dataset_summary() best practices
- max 2-3 lines
- focus on what questions it can answer
- mention key table names if helpful
- avoid redundant words

**good**: "uk broadband service pricing and plan details by isp and region. includes monthly costs, speeds, contract terms."

**bad**: "this dataset contains comprehensive information about various broadband tariff plans offered by different internet service providers across the united kingdom, including detailed pricing structures, service specifications, and contractual terms and conditions."

### get_db_info() structure
```python
def get_db_info():
    return f"""
    {DB_INFO}     # essential concepts, conventions, gotchas
    
    {DB_SCHEMA}   # table definitions with comments
    
    {SQL_EXAMPLES}  # CRITICAL: realistic examples showing common patterns
    """
```

### sql examples requirements
**essential for agent success** - examples teach agents how to query effectively:

- **format**: list of dictionaries with 'request' and 'response' keys
- **realistic requests**: actual questions users would ask
- **working sql**: queries that execute successfully  
- **common patterns**: joins, aggregations, filtering typical to this dataset
- **edge cases**: handle tricky aspects of the data structure

**example structure**:
```python
SQL_EXAMPLES = [
    {
        "request": "What are the cheapest FTTP plans available in London?",
        "response": """
        select 
            isp_name,
            plan_name, 
            monthly_cost,
            download_speed
        from tariff_core.reports.tariff_plans tp
        join tariff_core.reports.regions r using (region_code)
        where r.region_name = 'London'
        and tp.technology = 'fttp'
        order by monthly_cost asc
        limit 10
        """
    }
]
```

### context optimization checklist
- [ ] summary under 3 lines
- [ ] schema includes only essential columns
- [ ] **examples show common query patterns (3-5 required)**
- [ ] instructions prevent typical mistakes
- [ ] no redundant information
- [ ] clear naming conventions explained
- [ ] sanity check guidance included

### testing checklist
- [ ] module imports without errors
- [ ] functions return strings
- [ ] dataset appears in tool descriptions
- [ ] agent can assemble context successfully
- [ ] **sql examples execute without errors (test each one)**

