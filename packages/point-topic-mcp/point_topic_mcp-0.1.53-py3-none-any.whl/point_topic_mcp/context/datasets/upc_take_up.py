def get_dataset_summary():
    """This will be visible to the agent at all times, so keep it short, but let the agent know if the dataset can answer the question of the user."""
    return """
    UK broadband service take-up analytics with modeled subscriber estimates by ISP and technology at postcode level. 
    Algorithmic distribution of reported ISP totals using probability models. 
    Quarterly data with market share calculations.
    """


def get_db_info():
    return f"""
    {DB_INFO}

    {DB_SCHEMA}

    {SQL_EXAMPLES}
    """

TAKE_UP_DISTINCT_ISP_LIST = ['BT', 'Sky', 'TalkTalk', 'CityFibre TalkTalk', 'KCOM Lightstream', 'Virgin Cable', 'Gigaclear', 'Hyperoptic', 'Other']

DB_SCHEMA = """
-- Category 1: Latest quarterly distribution results (Wide Format)
-- These tables contain only the most recent quarter's data.

take_up_v3.report.rpt_postcode_lines_distribution_residential (
	postcode varchar(16777216) comment 'a single uk postcode.',
	lines float comment 'total number of residential lines in the postcode. sum of all isp_tech columns.',
	bt_fttc float comment 'number of lines for bt fttc.',
	bt_fttp float comment 'number of lines for bt fttp.',
	bt_adsl float comment 'number of lines for bt adsl.',
	sky_fttc float comment 'number of lines for sky fttc.',
	sky_fttp float comment 'number of lines for sky fttp.',
	sky_adsl float comment 'number of lines for sky adsl.',
	talktalk_opr_fttc float comment 'number of lines for talktalk (openreach) fttc.',
	talktalk_opr_fttp float comment 'number of lines for talktalk (openreach) fttp.',
	talktalk_opr_adsl float comment 'number of lines for talktalk (openreach) adsl.',
	talktalk_cf_fttp float comment 'number of lines for talktalk (cityfibre) fttp.',
	kcom_lightstream_fttp float comment 'number of lines for kcom lightstream fttp.',
	virgin_cable float comment 'number of lines for virgin cable.',
	gigaclear_fttp float comment 'number of lines for gigaclear fttp.',
	hyperoptic_fttp float comment 'number of lines for hyperoptic fttp.',
	other float comment 'number of lines for all other isps.',
	bt_market_share float comment 'market share for bt (all techs combined).',
	sky_market_share float comment 'market share for sky (all techs combined).',
	talktalk_market_share float comment 'market share for talktalk (all variants combined).',
	kcom_lightstream_market_share float comment 'market share for kcom lightstream.',
	virgin_market_share float comment 'market share for virgin cable.',
	gigaclear_market_share float comment 'market share for gigaclear.',
	hyperoptic_market_share float comment 'market share for hyperoptic.',
	other_market_share float comment 'market share for other isps.',
	quarter varchar(6) comment 'the reporting quarter, e.g., ''2025Q2''. contains only one value.',
	reported_at varchar(10) comment 'the reporting date, e.g., ''2025-06-01''. contains only one value.'
)

take_up_v3.report.rpt_postcode_lines_distribution_business (
	# this table has the exact same schema as the residential table above, but contains data for business lines.
)


-- Category 2: Full historical quarterly results (Long/Tidy Format)
-- These tables contain data for all available quarters, including the latest one.

take_up_v3.report.rpt_all_quarterly_results_residential (
	postcode varchar(16777216) comment 'a single uk postcode.',
	reported_at date comment 'the reporting date, e.g., ''2025-06-01''.',
	quarter varchar(6) comment 'the reporting quarter, e.g., ''2025Q2''.',
	operator_tech varchar(16777216) comment 'concatenated isp and technology, e.g., ''BT_FTTC''.',
	operator varchar(16777216) comment 'the name of the isp, e.g., ''BT'', ''Sky'', ''CityFibre TalkTalk''.',
	tech varchar(16777216) comment 'the technology type, e.g., ''fttp'', ''fttc''.',
	lines float comment 'number of residential lines for this specific operator_tech in this postcode and quarter. rows with lines=0 are not included.'
)

take_up_v3.report.rpt_all_quarterly_results_business (
	# this table has the exact same schema as the residential table above, but contains data for business lines.
)
"""



DB_INFO = f"""
This database contains quarterly model outputs based on Point Topic Availability data on the distribution of active broadband lines (subscriptions) for UK Internet Service Providers (ISPs) at the postcode level. The data is divided into residential and business lines.

There are two main categories of tables:
1.  **Latest Quarter Snapshot (Wide Format):** These tables (`rpt_postcode_lines_distribution_*`) provide a snapshot of the most recent quarter's data. Each postcode has a single row, and each ISP/technology combination is represented as a separate column. This format is useful for quickly comparing multiple ISPs within a postcode for the latest period.
2.  **Historical Time-Series (Long/Tidy Format):** These tables (`rpt_all_quarterly_results_*`) contain the complete historical data for all available quarters. The data is "unpivoted," with each row representing a single ISP/technology combination for a specific postcode and quarter. This is the preferred format for trend analysis, time-series queries, or aggregating data over multiple periods.

**Key Concepts & Querying Tips:**

*   **"Operator" means "ISP":** This is a critical convention. Throughout the database, the column named `operator` refers to the Internet Service Provider (e.g., 'Sky', 'BT'). Always treat it as the ISP.

*   **CRITICAL: Handling of Zero-Line Postcodes:**
    *   The wide-format tables (`rpt_postcode_lines_distribution_*`) will show a `0` value in a column if an ISP has no lines in that postcode.
    *   The long-format tables (`rpt_all_quarterly_results_*`) **OMIT** the row entirely if an ISP has zero lines in a postcode for a given quarter.
    *   This means a query like `SELECT * FROM rpt_all_quarterly_results_residential WHERE operator = 'BT'` will NOT return postcodes where BT has no presence. To find postcodes where an ISP has zero lines, you would need to use a `LEFT JOIN` from a complete list of postcodes or use the wide-format tables for the latest quarter.

*   **Residential vs. Business Data:** The data is split between residential and business lines. Ensure you are querying the correct table (`_residential` or `_business`) based on the user's request.

*   **Calculations & Relationships:**
    *   In the wide tables, `lines` is the sum of all individual ISP/technology columns (e.g., `bt_fttc`, `sky_fttp`, etc., up to `other`).
    *   Similarly, the sum of all `_market_share` columns for a given postcode will equal `1` (or be very close, allowing for floating-point inaccuracies).
    *   In the long tables, to get the total lines for a postcode in a specific quarter, you must `SUM(lines) GROUP BY postcode, quarter`.

*   **Operator & Technology Naming Conventions:**
    *   Pay close attention to the mapping between the raw `operator_tech` values and the cleaned `operator` and `tech` columns in the long-format tables.
    *   When filtering by operator name, use the proper-cased values found in the `operator` column. The user may provide a different variation (e.g., "talktalk"), which you should map correctly.
    *   The specific `operator` names are: {TAKE_UP_DISTINCT_ISP_LIST}.
    *   The `tech` column is always lowercase (e.g., 'fttp', 'fttc', 'adsl').
    *   The operator 'Other' has a `NULL` value for its `tech`.

*   **Date and Quarter Fields:**
    *   `quarter` is a `VARCHAR` in the format 'YYYYQN' (e.g., '2025Q2').
    *   `reported_at` represents the end of the quarter, formatted as 'YYYY-MM-01'. Be mindful of the data types (`VARCHAR` vs. `DATE`) when filtering.    
"""



SQL_EXAMPLES = [
    {
        "request": "What is the national market share for each ISP for residential lines in the latest quarter?",
        "response": """
-- This query uses the 'long' format table as it's much more efficient for aggregating by operator.
-- We calculate the total lines for each operator and then divide by the overall total lines to get the national market share.

-- First, filter the historical table to only include data from the most recent quarter.
with 

    latest_quarter_data as (
    select
        operator,
        lines
    from take_up_v3.report.rpt_all_quarterly_results_residential
    where quarter = (select max(quarter) from take_up_v3.report.rpt_all_quarterly_results_residential)
    ),

    -- Aggregate the lines per operator.
    operator_totals as (
    select
        operator,
        sum(lines) as total_lines
    from latest_quarter_data
    group by operator
    )

-- Final calculation of market share using the total lines for all operators.
select
    operator,
    total_lines,
    round(total_lines * 100.0 / sum(total_lines) over (), 2) as national_market_share_percentage
from operator_totals
order by national_market_share_percentage desc"""
    },
    {
        "request": "Show me the growth of FTTP technology for business lines over the last 4 quarters.",
        "response": """
-- Time-series analysis is a key use case for the 'long' historical tables.
-- It tracks the total number of FTTP lines quarter by quarter.

with 

    -- Select the quarterly data specifically for FTTP technology.
    fttp_business_lines as (
    select
        quarter,
        sum(lines) as total_fttp_lines
    from take_up_v3.report.rpt_all_quarterly_results_business
    where tech = 'fttp'
    group by quarter
    )

-- Use LAG window function to compare each quarter with the previous one to calculate growth.
-- Use QUALIFY to filter for the most recent 4 quarters after the window function is applied.
select
    quarter,
    total_fttp_lines,
    lag(total_fttp_lines, 1, 0) over (order by quarter) as previous_quarter_fttp_lines,
    total_fttp_lines - previous_quarter_fttp_lines as quarterly_growth
from fttp_business_lines
qualify dense_rank() over (order by quarter desc) <= 4
order by quarter desc"""
    },
    {
        "request": "In which postcodes does BT have over 60% market share for residential lines?",
        "response": """
-- This query is a perfect use case for the 'wide' latest results table.
-- The market share is pre-calculated, so we can simply filter on the bt_market_share column.

select
    postcode,
    lines as total_lines,
    (bt_fttp + bt_fttc + bt_adsl) as bt_total_lines,
    round(bt_market_share * 100, 2) as bt_market_share_percentage
from take_up_v3.report.rpt_all_quarterly_results_residential
where bt_market_share > 0.60
order by bt_market_share desc
limit 100"""
    },
    {
        "request": "For postcode 'SW1A 0AA', what is the ISP and technology breakdown for both residential and business lines in the most recent quarter?",
        "response": """
-- This query shows a detailed drill-down for a specific postcode, combining both residential and business data.
-- It uses the 'long' format tables and a UNION ALL to merge the results.

-- Define the latest quarter once to use in both parts of the union.
with 

    latest_quarter_info as (
    select 
        max(quarter) as latest_q 
    from take_up_v3.report.rpt_all_quarterly_results_residential
    )

select
    'Residential' as line_type,
    postcode,
    operator,
    tech,
    lines
from take_up_v3.report.rpt_all_quarterly_results_residential
where 
    postcode = 'SW1A 0AA' 
    and quarter = (select latest_q from latest_quarter_info)

union all

select
    'Business' as line_type,
    postcode,
    operator,
    tech,
    lines
from take_up_v3.report.rpt_all_quarterly_results_business
where 
    postcode = 'SW1A 0AA' 
    and quarter = (select latest_q from latest_quarter_info)

order by line_type, lines desc"""
    }
]