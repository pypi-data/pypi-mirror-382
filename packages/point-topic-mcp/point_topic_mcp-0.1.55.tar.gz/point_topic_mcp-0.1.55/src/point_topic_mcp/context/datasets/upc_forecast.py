def get_dataset_summary():
    "This will be visible to the agent at all times, so keep it short, but let the agent know if the dataset can answer the question of the user."
    return """
    UK broadband ISP availability and infrastructure forecasting data 
    with attractiveness scores and predicted operator footprint expansion by postcode. 
    Semi-annual forecasts.
    Data from 2025
    """


def get_db_info():
    return f"""
    {DB_INFO}

    {DB_SCHEMA}

    {SQL_EXAMPLES}
    """


DB_SCHEMA = """
forecast_v7.reports.all_general_attractiveness (
	postcode varchar(16777216) comment 'the uk postcode',
	time_since_last_upgrade number(35,6) comment 'attractiveness factor (0-1 scale): time elapsed since the last network upgrade in the area',
	affordability float comment 'attractiveness factor (0-1 scale): measure of the local population''s ability to afford broadband services',
	population_density float comment 'attractiveness factor (0-1 scale): measure of population density in the postcode area',
	digital_deprivation float comment 'attractiveness factor (0-1 scale): measure of the area''s need for better digital services',
	general_attractiveness float comment 'the overall attractiveness score, which is the sum of all other factor columns',
	quarter varchar(16777216) comment 'the quarter the report is for, format: YYYYQ[1-4], e.g., 2022Q3',
	reported_at date comment 'the date representation of the quarter, always the first day of the last month of the quarter, e.g., 2022-09-01 for 2022Q3'
)

forecast_v7.intermediate.int_forecast_output (
	postcode varchar(16777216) comment 'the uk postcode',
	operator varchar(16777216) comment 'the name of the broadband operator',
	present number(2,0) comment 'binary flag (0 or 1) indicating if the operator is forecast to have a presence (footprint) in the postcode by the end of the forecast period',
	reported_at varchar(10) comment 'the end date of the forecast period. CRITICAL: ''yyyy-06-01'' means end of year yyyy; ''yyyy-12-01'' means end of H1 of yyyy+1'
)
"""

UPC_FORECAST_DISTINCT_OPERATOR_LIST = [
    "CityFibre",
    "Community Fibre",
    "Connexin FTTP",
    "FW Networks",
    "Fibrus",
    "Full Fibre Ltd",
    "GNetwork",
    "Gigaclear",
    "Hyperoptic",
    "ITS FTTP",
    "KCOM Lightstream",
    "MS3 FTTP",
    "Netomnia You Fibre",
    "Openreach",
    "Trooli",
    "Virgin",
    "Voneus FTTP",
    "Zzoomm",
    "brsk FTTP",
    "nexfibre Virgin Media"
]

DB_INFO = f"""
This database contains data for forecasting broadband infrastructure deployment in the UK. It includes a table with postcode-level attractiveness scores and another with semi-annual footprint forecasts for key operators.

--- TABLE: all_general_attractiveness ---

This table provides a quarterly time-series of "attractiveness scores" for every UK postcode, indicating its potential for new broadband infrastructure investment.

Key Points:
- Granularity: Data is available for the full set of ~1.7 million UK postcodes for each quarter, starting from '2021Q2'.
- Time Columns:
  - `quarter`: The primary time dimension, formatted as 'YYYYQ[1-4]' (e.g., '2023Q4').
  - `reported_at`: A date representation of the quarter, always the first day of the last month of that quarter (e.g., '2023Q4' corresponds to '2023-12-01').
- Attractiveness Score:
  - The `general_attractiveness` column is the primary score.
  - CRITICAL: This score is a direct sum of the other factor columns (`time_since_last_upgrade`, `affordability`, `population_density`, `broadband_infrastructure`, `digital_deprivation`).
  - All factor columns are scaled from 0 to 1, where a higher value indicates a more positive contribution to the attractiveness score.

--- TABLE: int_forecast_output ---

This table contains semi-annual forecasts of network footprint for specific UK broadband operators up to the end of 2030.

Key Points:
- Granularity: The table contains a forecast for every UK postcode for each operator at each forecast period.
- Footprint Logic: The `present` column is a binary flag (1 for present, 0 for not present). It indicates if an operator is predicted to have a presence in that postcode by the end of the forecast period.
- Cumulative Growth: The footprint is cumulative. If an operator has `present` = 1 for a given postcode and `reported_at`, they will also have `present` = 1 for all subsequent `reported_at` dates. The network footprint only grows or stays the same.
- The data start from 2025

CRITICAL: The `reported_at` column does NOT represent when the forecast was made, but rather the point in time the forecast is FOR.

- `yyyy-06-01`: Forecast as of end of year **yyyy**.
- `yyyy-12-01`: Forecast as of end of H1 (first 6 months) of year **yyyy+1**.

Specifically, the `reported_at` column values and its meaning:
    - `2025-12-01`: mid 2026
    - `2026-06-01`: end of 2026
    - `2026-12-01`: mid 2027
    - `2027-06-01`: end of 2027
    - `2027-12-01`: mid 2028
    - `2028-06-01`: end of 2028
    - `2028-12-01`: mid 2029
    - `2029-06-01`: end of 2029
    - `2029-12-01`: mid 2030
    - `2030-06-01`: end of 2030 (largest time value of the forecast)

--- General Tips & Common Queries ---

1.  **Joining Tables**: The most common use case is to join these tables on `postcode`. Be mindful of the time columns. For example, you might want to join `all_general_attractiveness` from '2023Q4' (`reported_at` = '2023-12-01') with the `int_forecast_output` for the end of 2024 (`reported_at` = '2024-06-01') to see if high-attractiveness areas are being targeted for future builds.

2.  **Calculating New Build**: To find the postcodes where an operator is forecast to build in a specific period (e.g., the second half of 2027), you need to subtract the footprint of the previous period.
    - Example for H2 2027 build:
      1. Get postcodes where `present` = 1 for `reported_at` = '2027-06-01' (End of 2027).
      2. Get postcodes where `present` = 1 for `reported_at` = '2026-12-01' (Mid-2027).
      3. The difference between set (1) and set (2) represents the build during H2 2027. This can be done with a `LEFT JOIN` and checking for `NULL` or using `EXCEPT`.

3.  **Available Operators**: The operators available in the `int_forecast_output` table are:
{UPC_FORECAST_DISTINCT_OPERATOR_LIST}
"""


SQL_EXAMPLES = [
    {
        "request": "Show me the top 20 most attractive postcodes that Openreach is not expected to have a presence inby the middle of 2029.",
        "response": """
-- Finds high-potential areas without a forecasted presence from a major operator.
-- Gets the latest attractiveness scores for all postcodes.
-- Finds postcodes where 'Openreach' is forecasted to be present by mid-2029 => **reported_at='2028-12-01**.
-- Joins these sets and filters for postcodes in the attractive list but not in the Openreach list.

-- Find the most recent attractiveness score for each postcode
with 

    latest_attractiveness as (
    select
        postcode,
        general_attractiveness
    from forecast_v7.reports.all_general_attractiveness
    qualify row_number() over (partition by postcode order by reported_at desc) = 1
    ),

    -- Postcodes where Openreach is forecasted to be present by the middle of 2029 or **reported_at='2028-12-01**.
    openreach_future_footprint as (
    select distinct
        postcode
    from forecast_v7.intermediate.int_forecast_output
    where
        operator = 'Openreach'
        and reported_at = '2028-12-01'
        and present = 1
    )

select
    la.postcode,
    la.general_attractiveness
from latest_attractiveness as la
left join openreach_future_footprint as off
    on la.postcode = off.postcode
where
    off.postcode is null
order by
    la.general_attractiveness desc
limit 20"""
    },
    {
        "request": "Calculate the forecasted growth in number of postcodes for You Fibre between the end of middle 2026 and the end of 2028.",
        "response": """
-- Calculates the absolute and percentage growth for a specific operator over a multi-year forecast period.
-- Uses two CTEs to get the count of postcodes at two different points in time based on the 'reported_at' logic.
-- *reported_at='2025-12-01'* is the forecast for the middle of 2026.
-- *reported_at='2028-06-01'* is the forecast for the end of 2028.

with counts_by_period as (
    select
        count(distinct case when reported_at = '2025-12-01' then postcode end) as postcode_count_2026_mid,
        count(distinct case when reported_at = '2028-06-01' then postcode end) as postcode_count_2028
    from forecast_v7.intermediate.int_forecast_output
    where
        operator = 'Netomnia You Fibre'
        and reported_at in ('2025-12-01', '2028-06-01')
        and present = 1
)
select
    postcode_count_2026_mid,
    postcode_count_2028,
    postcode_count_2028 - postcode_count_2026_mid as absolute_growth,
    round(((postcode_count_2028 - postcode_count_2026_mid) / postcode_count_2026_mid) * 100, 2) as percentage_growth
from counts_by_period"""
    },
    {
        "request": "Which 10 postcodes have seen the largest increase in their 'general_attractiveness' score over the last year?",
        "response": """
-- Identifies postcodes with the most improved attractiveness.
-- Uses the LAG window function to get the attractiveness score from 4 quarters ago (1 year).
-- Careful handling of the quarter/date columns to ensure a correct comparison.

with attractiveness_over_time as (
    select
        postcode,
        quarter,
        reported_at,
        general_attractiveness,
        -- Get the score from 4 quarters prior for the same postcode
        lag(general_attractiveness, 4) over (partition by postcode order by reported_at) as previous_year_attractiveness
    from forecast_v7.reports.all_general_attractiveness
),

-- We only want to see the growth for the most recent period available
latest_period as (
    select *
    from attractiveness_over_time
    where reported_at = (select max(reported_at) from forecast_v7.reports.all_general_attractiveness)
)

select
    postcode,
    general_attractiveness as current_score,
    previous_year_attractiveness as last_year_score,
    general_attractiveness - previous_year_attractiveness as attractiveness_increase
from latest_period
where previous_year_attractiveness is not null -- Ensure we have data from a year ago to compare
order by attractiveness_increase desc
limit 10"""
    },
    {
        "request": "For all postcodes that CityFibre is forecasted to build in during 2027, what is their average attractiveness profile in the latest quarter?",
        "response": """
-- Identifies the set of postcodes newly entered by CityFibre in 2027 by comparing their footprint at the end of 2026 (**reported_at = '2026-06-01'**) and 2027 (**reported_at = '2027-06-01'**).
-- Joins these postcodes to the latest attractiveness data to calculate the average for each factor.

with cityfibre_eoy_2026 as (
    select postcode
    from forecast_v7.intermediate.int_forecast_output
    where operator = 'CityFibre' and present = 1 and reported_at = '2026-06-01'
),

cityfibre_eoy_2027 as (
    select postcode
    from forecast_v7.intermediate.int_forecast_output
    where operator = 'CityFibre' and present = 1 and reported_at = '2027-06-01'
),

-- Find postcodes that are in the 2027 list but not the 2026 list
new_builds_2027 as (
    select postcode from cityfibre_eoy_2027
    except
    select postcode from cityfibre_eoy_2026
),

latest_attractiveness as (
    select
        postcode,
        time_since_last_upgrade,
        affordability,
        population_density,
        broadband_infrastructure,
        digital_deprivation
    from forecast_v7.reports.all_general_attractiveness
    qualify row_number() over (partition by postcode order by reported_at desc) = 1
)

select
    avg(la.time_since_last_upgrade) as avg_time_since_last_upgrade,
    avg(la.affordability) as avg_affordability,
    avg(la.population_density) as avg_population_density,
    avg(la.broadband_infrastructure) as avg_broadband_infrastructure,
    avg(la.digital_deprivation) as avg_digital_deprivation
from latest_attractiveness as la
join new_builds_2027 as nb on la.postcode = nb.postcode"""
    },
    {
        "request": "Which operator is forecasted to have the largest footprint (most postcodes) by the end of 2030?",
        "response": """
select
    operator,
    count(postcode) as total_postcodes_present
from forecast_v7.intermediate.int_forecast_output
where
    reported_at = '2030-06-01' -- Forecast period for end of year 2030
    and present = 1
group by
    operator
order by
    total_postcodes_present desc
limit 1"""
    }
]
