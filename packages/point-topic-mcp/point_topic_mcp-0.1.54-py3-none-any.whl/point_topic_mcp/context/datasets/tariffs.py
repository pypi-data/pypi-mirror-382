def get_dataset_summary():
    """This will be visible to the agent at all times, so keep it short."""
    return """
    uk broadband service pricing and plan details by isp and period. 
    includes monthly costs, speeds, contract terms, and postcode mappings for geographic analysis.
    quarterly snapshots with change tracking via group_id.
    """

def get_db_info():
    return f"""
    {DB_INFO}

    {DB_SCHEMA}

    {SQL_EXAMPLES}
    """

DB_INFO = """
UK broadband tariff pricing data with geographic postcode mapping. Quarterly snapshots from 2021Q2-2025Q3.

CRITICAL: This dataset has complex operator name mappings between tariff source and UPC footprint data.

Key Tables and Data Flow:
- research.reports.rpt_tariff: global raw tariff data (267k records, 99 countries)
- upc_client._src_research_app.upc_tariffs_time_series: uk-filtered tariffs with operator mapping (7.5k records, 78 operators)  
- upc_client._src_research_app.upc_tariff_postcode_time_series: postcode-tariff mapping (978M records, 1.7M postcodes)
- upc_core.reports.upc_output: postcode demographics for geographic analysis

PERFORMANCE WARNING: Postcode mapping table has 978M records. Always filter by period and limit geographic scope.

Period Format: quarters like '2024Q1', '2025Q2'. Current period typically '2025Q2'.
Change Tracking: group_id persists across periods, tariff_id changes each period.

Essential Filtering:
- country = 'United Kingdom' for uk analysis (research.reports table only)
- period = '2025Q2' for current data (or specify period)
- type = 'Standalone' to exclude bundles, or type = 'Bundle' for bundles
- monthly_subscription is not null to exclude plans without pricing

Operator Name Complexity:
- tariff operators (e.g., "Sky UK") != upc operators (e.g., "Sky", "Sky FTTP")
- upc_isp field in processed tables provides standardized names
- 78 unique operators in UK processed data vs 186 in raw data

Geographic Analysis Pattern:
tariffs → upc_tariff_postcode_time_series → upc_output (for demographics/regions)

Common Gotchas:
1. tech field can contain comma-separated values (e.g., 'FTTP, FWA')
2. large table sizes require period/operator/region filtering
3. contract_length is varchar (can be null or empty string)
4. pricing fields: monthly_subscription (core), activation, installation, equipment_fee
"""

DB_SCHEMA = """
research.reports.rpt_tariff (
    tariff_id varchar comment 'unique identifier for tariff snapshot',
    group_id varchar comment 'persistent identifier across periods for change tracking',
    operator varchar comment 'isp name (global data, varies from upc naming)',
    date timestamp_ntz comment 'report date',
    period varchar comment 'quarterly period (e.g. 2024Q1)', 
    country varchar comment 'country (filter: United Kingdom for uk data)',
    domain varchar comment 'residential/business',
    name varchar comment 'tariff/plan name',
    tech varchar comment 'technology (can be comma-separated)',
    type varchar comment 'standalone/bundle',
    monthly_subscription float comment 'monthly price in local currency',
    downstream_mbs float comment 'download speed mbps',
    upstream_mbs float comment 'upload speed mbps',
    contract_length varchar comment 'contract months (varchar field)',
    broadband_included boolean comment 'true for broadband plans',
    tv varchar comment 'tv service details',
    monthly_tv_addon float comment 'tv addon monthly cost',
    notes varchar comment 'special offers and conditions'
)

upc_client._src_research_app.upc_tariffs_time_series (
    tariff_id varchar comment 'unique identifier linking to raw tariff data',
    operator varchar comment 'original operator name from research data',
    upc_isp varchar comment 'standardized operator name matching upc footprint data',
    upc_tech varchar comment 'standardized technology name', 
    date timestamp_ntz comment 'report date',
    period varchar comment 'quarterly period (e.g. 2025Q2)',
    country varchar comment 'always United Kingdom for this table',
    domain varchar comment 'residential/business',
    name varchar comment 'tariff/plan name',
    tech varchar comment 'original technology string',
    type varchar comment 'standalone/bundle',
    monthly_subscription float comment 'monthly price gbp',
    downstream_mbs float comment 'download speed mbps',
    upstream_mbs float comment 'upload speed mbps',
    contract_length varchar comment 'contract months (varchar)',
    broadband_included boolean comment 'always true for this filtered table',
    tv varchar comment 'tv service included',
    monthly_tv_addon float comment 'tv addon cost',
    fixed_telephony varchar comment 'phone service included',
    mobile_telephony varchar comment 'mobile service included',
    notes varchar comment 'plan details and offers'
)

upc_client._src_research_app.upc_tariff_postcode_time_series (
    postcode varchar comment 'uk postcode',
    tariff_id varchar comment 'links to tariff tables',
    upc_isp varchar comment 'standardized operator name',
    upc_tech varchar comment 'standardized technology',
    period varchar comment 'quarterly period'
)
"""

SQL_EXAMPLES = [
    {
        'request': 'What are the cheapest standalone broadband plans available in London?',
        'response': """
select 
    t.upc_isp as operator,
    t.name as plan_name,
    t.monthly_subscription as monthly_price,
    t.downstream_mbs as download_speed,
    t.upstream_mbs as upload_speed,
    count(distinct tp.postcode) as london_postcodes_covered
from upc_client._src_research_app.upc_tariffs_time_series t
join upc_client._src_research_app.upc_tariff_postcode_time_series tp using (tariff_id, period)
join upc_core.reports.upc_output u using (postcode)
where t.period = '2025Q2'
    and t.type = 'Standalone'
    and t.monthly_subscription is not null
    and u.government_region = 'London'
group by t.tariff_id, t.upc_isp, t.name, t.monthly_subscription, t.downstream_mbs, t.upstream_mbs
order by t.monthly_subscription asc
limit 10
        """
    },
    {
        'request': 'Compare average broadband pricing across UK regions for the current period',
        'response': """
select 
    u.government_region,
    count(distinct t.tariff_id) as available_plans,
    count(distinct t.upc_isp) as operators_present,
    round(avg(t.monthly_subscription), 2) as avg_monthly_price,
    round(min(t.monthly_subscription), 2) as cheapest_plan,
    round(max(t.monthly_subscription), 2) as most_expensive,
    round(avg(t.downstream_mbs), 0) as avg_download_speed
from upc_client._src_research_app.upc_tariffs_time_series t
join upc_client._src_research_app.upc_tariff_postcode_time_series tp using (tariff_id, period)
join upc_core.reports.upc_output u using (postcode)
where t.period = '2025Q2'
    and t.type = 'Standalone'
    and t.monthly_subscription is not null
group by u.government_region
order by avg_monthly_price desc
        """
    },
    {
        'request': 'Show me which operators offer gigabit speeds and their pricing',
        'response': """
select 
    t.upc_isp as operator,
    count(distinct t.tariff_id) as gigabit_plans,
    round(avg(t.monthly_subscription), 2) as avg_gigabit_price,
    round(min(t.monthly_subscription), 2) as cheapest_gigabit,
    round(avg(t.downstream_mbs), 0) as avg_download_speed,
    round(avg(t.upstream_mbs), 0) as avg_upload_speed
from upc_client._src_research_app.upc_tariffs_time_series t
where t.period = '2025Q2'
    and t.type = 'Standalone'
    and t.downstream_mbs >= 1000
    and t.monthly_subscription is not null
group by t.upc_isp
having count(distinct t.tariff_id) >= 1
order by avg_gigabit_price asc
        """
    },
    {
        'request': 'How have BT tariff prices changed over the last 4 quarters?',
        'response': """
with bt_pricing as (
    select 
        t.period,
        t.name as plan_name,
        t.monthly_subscription,
        t.downstream_mbs,
        lag(t.monthly_subscription) over (partition by t.group_id order by t.period) as prev_price
    from research.reports.rpt_tariff t
    where t.operator = 'BT Group'
        and t.country = 'United Kingdom'
        and t.period in ('2024Q3', '2024Q4', '2025Q1', '2025Q2')
        and t.type = 'Standalone'
        and t.broadband_included = true
        and t.monthly_subscription is not null
)

select 
    period,
    count(*) as total_plans,
    round(avg(monthly_subscription), 2) as avg_price,
    count(case when prev_price is not null and monthly_subscription != prev_price then 1 end) as price_changes,
    round(avg(case when prev_price is not null then monthly_subscription - prev_price end), 2) as avg_price_change
from bt_pricing
group by period
order by period
        """
    },
    {
        'request': 'What broadband plans are available in postcodes starting with M1 (Manchester area)?',
        'response': """
select 
    t.upc_isp as operator,
    t.name as plan_name,
    t.monthly_subscription as monthly_price,
    t.downstream_mbs as download_speed,
    t.type as plan_type,
    count(distinct tp.postcode) as m1_postcodes_covered
from upc_client._src_research_app.upc_tariffs_time_series t
join upc_client._src_research_app.upc_tariff_postcode_time_series tp using (tariff_id, period)
where t.period = '2025Q2'
    and tp.postcode like 'M1%'
    and t.monthly_subscription is not null
group by t.tariff_id, t.upc_isp, t.name, t.monthly_subscription, t.downstream_mbs, t.type
order by t.monthly_subscription asc
limit 20
        """
    }
]
