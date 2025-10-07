# context window optimization analysis

## current dataset summaries (always visible to agents)

**upc**: 
> UK broadband infrastructure availability data at postcode level. Monthly snapshots showing operator footprint and premises coverage (not subscriber numbers). UPC_OUTPUT table has a row for each postcode, with geographic, demograpgic and broadband availability data. FACT_OPERATOR table has a row for each postcode, operator and technology, with the fastest up and down speeds.

**upc_take_up**:
> UK broadband service take-up analytics with modeled subscriber estimates by ISP and technology at postcode level. Algorithmic distribution of reported ISP totals using probability models. Quarterly data with market share calculations. RPT_POSTCODE_LINES_DISTRIBUTION_RESIDENTIAL table has a row for each postcode, with the total number of residential lines for each ISP and technology. [continues...]

**upc_forecast**:
> UK broadband ISP availability and infrastructure forecasting data with attractiveness scores and predicted operator footprint expansion by postcode. Semi-annual forecasts. Data from 2025

## optimization recommendations

### current issues
1. **upc summary is 65 words** - should be max 20-25 words
2. **upc_take_up is 85+ words** - extremely verbose for always-visible content
3. **redundant explanations** - table structures don't need full descriptions in summaries
4. **technical jargon** without context value

### optimized summaries

**upc** (current: 65 words → optimized: 18 words):
```
UK broadband infrastructure availability data at postcode level. 
Monthly snapshots showing operator footprint and premises coverage.
```

**upc_take_up** (current: 85+ words → optimized: 22 words):
```
UK broadband subscriber estimates by ISP and technology at postcode level. 
Quarterly modeled data with market share calculations.
```

**upc_forecast** (current: 28 words → good as-is):
```
UK broadband infrastructure forecasting data with attractiveness scores 
and predicted operator footprint expansion by postcode. Semi-annual forecasts.
```

### new tariffs dataset (optimized):
```
UK broadband service pricing and plan details by ISP and region. 
Monthly costs, speeds, contract terms.
```

## full context optimization (get_db_info)

### current bloat patterns
1. **excessive examples** - upc.py has 6 examples (416 lines)
2. **verbose schemas** - detailed comments for every column
3. **redundant instructions** - same concepts repeated
4. **over-documentation** - tutorial-level explanations

### streamlined approach for new datasets
1. **limit examples to 3-4 max**
2. **essential schema only** - key columns with brief comments
3. **focused instructions** - common mistakes and key concepts only
4. **remove redundant UK facts** - already in general instructions

### token estimation
- **current upc.py**: ~2,500 tokens
- **optimized tariffs**: target ~1,200 tokens (50% reduction)

## implementation strategy for tariffs

### summary (max 20 words)
```
UK broadband service pricing and plan details by ISP. 
Monthly costs, speeds, contract terms, regional variations.
```

### db_info structure (condensed)
```python
DB_INFO = """
Brief overview of tariff data structure and key concepts.
Critical naming conventions and common query patterns.
Essential gotchas and performance tips.
"""

DB_SCHEMA = """
# only 2-3 most important tables
# essential columns with brief comments
# skip redundant geographic fields
"""

SQL_EXAMPLES = [
    # 3 examples max
    # focus on common use cases
    # shorter queries with clear purpose
]
```

## general principles for all new datasets

1. **summary function**: absolute max 30 words, target 20
2. **schema**: essential tables/columns only
3. **examples**: 3-4 realistic queries, no more
4. **instructions**: focus on mistakes prevention
5. **eliminate redundancy**: don't repeat general instructions

## context window savings estimate

- **current approach**: ~8,000 tokens per dataset
- **optimized approach**: ~4,000 tokens per dataset  
- **50% reduction** while maintaining functionality

this becomes critical as we add more datasets (tariffs, future additions).




