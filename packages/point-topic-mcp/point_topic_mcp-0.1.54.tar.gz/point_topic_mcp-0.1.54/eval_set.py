evals = {
    "questions": [
        {
            "id": 1,
            "content": "What's Virgin Media's total market reach right now across the UK? I want to know the percentage of all properties they could potentially sell to.",
            "target_db": "upc",
            "answer": """
                Virgin Media's current total market reach across the UK is as follows:
                    - Virgin Media can potentially sell to 16,856,889 premises.
                    - The total number of premises in the UK is 33,596,842.
                    - This means Virgin Media's network is available to 50.17% of all UK properties.
                This figure represents their availability footprint (i.e., the percentage of all UK premises that could buy a Virgin Media service if they chose to).
            """,
            "sql_query": """
                -- Calculate Virgin Media's total market reach (availability footprint) as a percentage of all UK premises
                with 
                    -- Get all postcodes where Virgin Media is present (either 'Virgin Cable' or 'Virgin Media RFOG')
                    virgin_postcodes as (
                        select distinct postcode
                        from upc_core.reports.fact_operator
                        where operator in ('Virgin Cable', 'Virgin Media RFOG')
                    ),
                    -- Sum premises in those postcodes for Virgin Media's footprint
                    virgin_footprint as (
                        select sum(u.premises) as virgin_premises
                        from virgin_postcodes v
                        join upc_core.reports.upc_output u using (postcode)
                    ),
                    -- Get total UK premises from upc_output
                    total_uk as (
                        select sum(premises) as total_premises
                        from upc_core.reports.upc_output
                    )
                select 
                    commaify(v.virgin_premises) as virgin_media_premises,
                    commaify(t.total_premises) as total_uk_premises,
                    round((v.virgin_premises / t.total_premises) * 100, 2) as virgin_media_market_reach_percentage
                from virgin_footprint v, total_uk t
            """
        },
        {
            "id": 2,
            "content": "Let's talk about the smaller internet providers, not the big ones like Openreach or Virgin. How many homes in total can these altnet currently sell their services to?",
            "target_db": "upc",
            "answer": """
                Currently, alternative network providers (altnets)—excluding the big names like Openreach (BT) and Virgin Media—can sell their services to approximately 16,605,117 UK households. 
                This figure represents the total number of homes within the footprint of all altnets combined, based on the latest available data.
            """,
            "sql_query": """
                -- Calculate total number of households that can be served by altnets (excluding Openreach and Virgin Media)
                with 
                    altnet_operators as (
                        select distinct operator
                        from upc_core.reports.fact_operator
                        where operator not in ('BT','Sky','TalkTalk','Vodafone','Virgin Cable','Virgin Media RFOG')
                    ),
                    
                    altnet_postcodes as (
                        select distinct f.postcode
                        from upc_core.reports.fact_operator f
                        where f.operator in (select operator from altnet_operators)
                    )
                select commaify(round(sum(u.households),0)) as total_households_served_by_altnets
                from upc_core.reports.upc_output u
                join altnet_postcodes a on u.postcode = a.postcode
            """
        },
        {
            "id": 3,
            "content": "Which parts of the country have the best access to gigabit-speed internet? I want to see the top 5 regions, ranked by how many properties can get those speeds.",
            "target_db": "upc",
            "answer": """
                The top 5 UK regions with the best access to gigabit-speed internet (ranked by the number of properties able to get those speeds) are: 
                    1. South East 3,533,275 premises 
                    2. London 3,509,028 premises 
                    3. North West 3,294,467 premises 
                    4. West Midlands 2,569,996 premises 
                    5. East of England  2,494,091 premises. 
                These regions have the highest number of properties with access to gigabit-speed broadband (≥1000 Mbps).
            """,
            "sql_query": """
                -- Top 5 UK regions by number of premises with gigabit-speed broadband available
                -- Gigabit defined as fastest_down >= 1000 Mbps
                with gigabit_postcodes as (
                    select 
                        u.government_region,
                        u.premises,
                        max(f.fastest_down) as max_down
                    from upc_core.reports.upc_output u
                    join upc_core.reports.fact_operator f using (postcode)
                    group by u.government_region, u.postcode, u.premises
                    having max(f.fastest_down) >= 1000
                )
                select 
                    government_region,
                    sum(premises) as premises_with_gigabit
                from gigabit_postcodes
                where government_region is not null
                group by government_region
                order by premises_with_gigabit desc
                limit 5;
            """
        },
        {
            "id": 4,
            "content": "I'm interested in new infrastructure. Can you tell me how many postcodes got their very first full fibre connection sometime in the last year?",
            "target_db": "upc",
            "answer": """
                In the last year, 183,383 UK postcodes received their very first full fibre (FTTP) connection. 
                This represents the number of unique postcodes where FTTP became available for the first time during that period.
            """,
            "sql_query": """
                -- Find postcodes that got their first FTTP connection in the last year
                with 
                    fttp_first_seen as (
                        select 
                            postcode,
                            min(reported_at) as first_fttp_date
                        from upc_core.reports.fact_operator_time_series
                        where tech like '%fttp%'
                        group by postcode
                    ),
                    last_year as (
                        select dateadd(year, -1, max(reported_at)) as one_year_ago, max(reported_at) as latest
                        from upc_core.reports.fact_operator_time_series
                    )
                select 
                    count(distinct f.postcode) as postcodes_first_fttp_last_year
                from fttp_first_seen f
                join last_year l on f.first_fttp_date > l.one_year_ago and f.first_fttp_date <= l.latest
            """
        },
        {
            "id": 5,
            "content": "What's the expansion plan for Community Fibre? How many brand new postcodes are they expected to enter during the first six months of 2028?",
            "target_db": "upc_forecast",
            "answer": """
                Community Fibre is forecasted to enter 135,276 brand new postcodes during the first six months of 2028. 
                This figure represents the number of postcodes where Community Fibre is expected to have a presence at the end of H1 2028 that they did not have at the end of 2027, according to the latest infrastructure expansion forecasts.
            """,
            "sql_query": """
                -- Calculate the number of brand new postcodes Community Fibre is forecasted to enter in H1 2028
                -- H1 2028 = reported_at = '2027-12-01'
                -- Need to compare footprint at end of 2027 (2027-06-01) vs H1 2028 (2027-12-01)

                with cf_eoy_2027 as (
                    select postcode
                    from forecast_v7.intermediate.int_forecast_output
                    where operator = 'Community Fibre' and present = 1 and reported_at = '2027-06-01'
                ),

                cf_h1_2028 as (
                    select postcode
                    from forecast_v7.intermediate.int_forecast_output
                    where operator = 'Community Fibre' and present = 1 and reported_at = '2027-12-01'
                )

                select count(*) as new_postcodes_h1_2028
                from (
                    select postcode from cf_h1_2028
                    except
                    select postcode from cf_eoy_2027
                )
            """
        },
        {
            "id": 6,
            "content": "Looking ahead to the middle of 2027, where do we predict CityFibre and Openreach will be competing head-to-head? I mean, in how many postcodes will they both be operating?",
            "target_db": "upc_forecast",
            "answer": """
                By the middle of 2027, CityFibre and Openreach are forecasted to be competing head-to-head in approximately 323,760 UK postcodes—meaning both operators are predicted to have a presence in those postcodes at that time.
            """,
            "sql_query": """
                -- Find the number of postcodes where BOTH CityFibre and Openreach are forecasted to be present at mid-2027
                with 
                    cityfibre_2027 as (
                        select postcode
                        from forecast_v7.intermediate.int_forecast_output
                        where operator = 'CityFibre' and present = 1 and reported_at = '2026-12-01'
                    ),
                    openreach_2027 as (
                        select postcode
                        from forecast_v7.intermediate.int_forecast_output
                        where operator = 'Openreach' and present = 1 and reported_at = '2026-12-01'
                    )
                select count(*) as overlapping_postcodes
                from cityfibre_2027 cf
                join openreach_2027 orh on cf.postcode = orh.postcode
            """
        },
        {
            "id": 7,
            "content": "Let's analyze brsk's future strategy. For all the areas they plan to build in between the end of 2025 and 2026, how digitally needy are those places on average?",
            "target_db": "upc_forecast",
            "answer": """
                For all the areas that brsk is forecasted to newly build in between the end of 2025 and the end of 2026, the average digital deprivation score is approximately 0.59 (on a 0–1 scale, where higher means greater digital need). 
                This indicates that, on average, brsk is targeting areas with a moderate to high level of digital need for its 2026 expansion.
            """,
            "sql_query": """
                -- Step 1: Identify postcodes where brsk FTTP is forecasted to build between end of 2025 and end of 2026
                -- Step 2: Join to latest digital deprivation scores for those postcodes
                -- Step 3: Calculate the average digital deprivation for these areas

                with 
                -- Get brsk FTTP footprint at end of 2025
                brsk_2025 as (
                    select postcode
                    from forecast_v7.intermediate.int_forecast_output
                    where operator = 'brsk FTTP' and present = 1 and reported_at = '2025-06-01'
                ),
                -- Get brsk FTTP footprint at end of 2026
                brsk_2026 as (
                    select postcode
                    from forecast_v7.intermediate.int_forecast_output
                    where operator = 'brsk FTTP' and present = 1 and reported_at = '2026-06-01'
                ),
                -- Find postcodes that are new in 2026 (i.e., built between end 2025 and end 2026)
                brsk_new_2026 as (
                    select postcode from brsk_2026
                    except
                    select postcode from brsk_2025
                ),
                -- Get the latest digital deprivation score for each postcode
                latest_attractiveness as (
                    select postcode, digital_deprivation
                    from forecast_v7.reports.all_general_attractiveness
                    qualify row_number() over (partition by postcode order by reported_at desc) = 1
                )
                select 
                    avg(la.digital_deprivation) as avg_digital_deprivation
                from latest_attractiveness la
                join brsk_new_2026 b on la.postcode = b.postcode
            """
        },
        {
            "id": 8,
            "content": "I want to find areas that are highly connected but aren't served by Sky. Can you show me the top 10 postcodes with the most active residential internet connections, but where Sky has no customers at all?",
            "target_db": "take_up",
            "answer": """
                Here are the top 10 UK postcodes with the most active residential internet connections, but where Sky has no customers at all (across all technologies):

                | Postcode | Total Residential Lines |
                |----------|------------------------|
                | PE11 3QG | 89                     |
                | DE22 3XH | 89                     |
                | HP23 6JF | 89                     |
                | M15 6AA  | 89                     |
                | EH4 4GR  | 89                     |
                | BN3 1RR  | 89                     |
                | M14 6ZA  | 89                     |
                | SW8 5JE  | 89                     |
                | BT92 0LU | 89                     |
                | CF32 0QF | 89                     |

                These areas are highly connected but have zero Sky residential customers.
            """,
            "sql_query": """
                -- Find the top 10 postcodes with the most active residential internet connections where Sky has no customers at all
                -- Use the wide-format table for the latest quarter, as it includes zero-line ISPs

                select
                    postcode,
                    lines as total_residential_lines
                from take_up_v3.report.rpt_postcode_lines_distribution_residential
                where 
                    (coalesce(sky_fttc,0) + coalesce(sky_fttp,0) + coalesce(sky_adsl,0)) = 0 -- Sky has no lines of any tech
                    and lines > 0 -- Only consider postcodes with active connections
                order by total_residential_lines desc
                limit 10
            """
        },
        {
            "id": 9,
            "content": "What's the total number of Virgin Cable subscribers who are on their best full fibre service? I need the grand total, including both home and business accounts.",
            "target_db": "take_up",
            "answer": """
                The total number of Virgin Cable subscribers on their best full fibre (FTTP) service, including both home (residential) and business accounts, is:

                - Residential lines: 0
                - Business lines: 0
                - Grand total: 0

                This means that, according to the latest available data, there are currently no reported Virgin Cable FTTP (full fibre) subscribers in the UK. Virgin's main service is still their DOCSIS-based cable, and their FTTP footprint (if any) is not yet reflected in the national take-up data.
            """,
            "sql_query": """
                -- Get the latest quarter for both residential and business tables
                with latest_quarter as (
                    select max(quarter) as qtr from take_up_v3.report.rpt_all_quarterly_results_residential
                ),

                -- Virgin's best full fibre service is FTTP (not cable). The operator name is 'Virgin Cable', tech is 'fttp'.
                virgin_fttp_res as (
                    select sum(lines) as res_lines
                    from take_up_v3.report.rpt_all_quarterly_results_residential
                    where operator = 'Virgin Cable' and tech = 'fttp' and quarter = (select qtr from latest_quarter)
                ),
                virgin_fttp_bus as (
                    select sum(lines) as bus_lines
                    from take_up_v3.report.rpt_all_quarterly_results_business
                    where operator = 'Virgin Cable' and tech = 'fttp' and quarter = (select qtr from latest_quarter)
                )
                select 
                    coalesce(r.res_lines,0) as residential_lines,
                    coalesce(b.bus_lines,0) as business_lines,
                    coalesce(r.res_lines,0) + coalesce(b.bus_lines,0) as total_virgin_fttp_lines
                from virgin_fttp_res r
                cross join virgin_fttp_bus b
            """
        },
        {
            "id": 10,
            "content": "How has BT's customer base for their older, non-full-fibre service been changing? Show me the quarter-over-quarter change in home subscribers over the last year and a half.",
            "target_db": "take_up",
            "answer": """
                Here is the quarter-over-quarter change in BT's residential (home) subscribers for their older, non-full-fibre services (ADSL and FTTC) over the last year and a half:

                | Quarter | BT Old-Tech Home Subscribers | QoQ Change |
                |---------|-----------------------------|------------|
                | 2025Q1  | 5,583,261                   | -242,332   |
                | 2024Q4  | 5,825,593                   | -1,404,414 |
                | 2024Q3  | 7,230,007                   | +1,527,258 |
                | 2024Q2  | 5,702,749                   | -175,336   |
                | 2024Q1  | 5,878,085                   | -242,850   |
                | 2023Q4  | 6,120,935                   | -391,776   |

                Key insights:
                - BT's old-tech (ADSL + FTTC) home subscriber base has generally been declining, with the exception of a large increase in 2024Q3.
                - The most recent quarters (2024Q4 and 2025Q1) show significant declines, especially in 2024Q4.
                - This trend reflects the ongoing migration from older copper-based services to full fibre (FTTP) and other technologies.
            """,
            "sql_query": """
                -- This query calculates the quarter-over-quarter change in BT's residential (home) subscribers for their older, non-full-fibre services (ADSL and FTTC) over the last 6 quarters (1.5 years).
                -- We exclude FTTP (full fibre) and sum only ADSL and FTTC lines for BT.

                with 
                    bt_old_tech_lines as (
                        select
                            quarter,
                            sum(lines) as bt_non_full_fibre_lines
                        from take_up_v3.report.rpt_all_quarterly_results_residential
                        where operator = 'BT'
                        and tech in ('adsl', 'fttc')
                        group by quarter
                    ),
                    ranked as (
                        select
                            quarter,
                            bt_non_full_fibre_lines,
                            lag(bt_non_full_fibre_lines) over (order by quarter) as prev_quarter_lines
                        from bt_old_tech_lines
                        qualify dense_rank() over (order by quarter desc) <= 6
                    )
                select
                    quarter,
                    bt_non_full_fibre_lines as bt_old_tech_home_subscribers,
                    bt_non_full_fibre_lines - prev_quarter_lines as qoq_change
                from ranked
                order by quarter desc;
            """
        },
        {
            "id": 11,
            "content": "If we identify the 10 most promising postcodes for new broadband investment right now, what does the actual full fibre coverage look like in those specific areas today?",
            "target_db": "cross_db",
            "answer": """
                Here is what the actual full fibre (FTTP) coverage looks like today in the 10 most promising postcodes for new broadband investment (based on the latest attractiveness scores):

                Of the top 10 postcodes, only 2 have any current FTTP coverage:

                1. HU6 9AL
                - Operators: KCOM Lightstream, MS3 FTTP
                - Coverage: 49 premises (all households, no business sites)
                - Both operators cover the same 49 premises.

                2. ST1 3DW
                - Operator: Freedom Fibre FTTP
                - Coverage: 1.09 premises (all business sites, no households)

                The other 8 most promising postcodes currently have no FTTP (full fibre) coverage by any operator.

                Summary:
                - Most of the top 10 high-potential postcodes are still unserved by full fibre.
                - Where FTTP is present, it is either fully residential (HU6 9AL) or very limited and business-focused (ST1 3DW).
            """,
            "sql_query": """
                -- Step 1: Identify the 10 most promising postcodes for new broadband investment (highest attractiveness score, latest quarter)
                with top_attractive_postcodes as (
                    select postcode
                    from forecast_v7.reports.all_general_attractiveness
                    qualify row_number() over (partition by postcode order by reported_at desc) = 1
                    order by general_attractiveness desc
                    limit 10
                ),
                -- Step 2: Get current FTTP (full fibre) coverage for these postcodes
                fttp_coverage as (
                    select 
                        f.postcode,
                        f.operator,
                        f.tech,
                        u.premises,
                        u.households,
                        u.bus_sites_total
                    from upc_core.reports.fact_operator f
                    join upc_core.reports.upc_output u on f.postcode = u.postcode
                    where lower(f.tech) like '%fttp%'
                        and f.postcode in (select postcode from top_attractive_postcodes)
                )
                select 
                    postcode,
                    operator,
                    tech,
                    premises,
                    households,
                    bus_sites_total
                from fttp_coverage
                order by postcode, operator
            """
        },
        {
            "id": 12,
            "content": "Let's focus on Hyperoptic's strongholds. For all the postcodes where they currently have at least 50 home internet subscribers, how much is their network predicted to expand in those same areas between the end of 2024 and the end of 2027?",
            "target_db": "cross_db",
            "answer": """
                For all UK postcodes where Hyperoptic currently has at least 50 residential home internet subscribers, their network is forecasted to expand significantly between the end of 2024 and the end of 2027:

                - In every postcode meeting your criteria, Hyperoptic is forecasted to have no network presence at the end of 2024 (present_2024 = 0), but to have a presence by the end of 2027 (present_2027 = 1).
                - This means Hyperoptic is predicted to expand its network into all of these stronghold postcodes during this period.

                **Summary:**
                - Number of stronghold postcodes (with ≥50 current Hyperoptic subscribers) forecasted to gain Hyperoptic network presence between end-2024 and end-2027: **Over 300 postcodes** (see sample list below).
                - In all these postcodes, Hyperoptic is forecasted to go from no network presence (by the model’s definition) at end-2024 to full presence by end-2027.

                **Sample of affected postcodes:**
                - AL1 3UP
                - IG1 2JT
                - M3 7DZ
                - B25 8FG
                - NW9 6GJ
                - ...and many more (full list available on request).

                **Interpretation:**  
                Hyperoptic is expected to expand its official network footprint into all of its current strongholds (where it already has at least 50 subscribers) between the end of 2024 and the end of 2027, according to the forecast data.

                If you want a count, a breakdown by region, or the full postcode list, let me know!
            """,
            "sql_query": """
                -- Step 1: Identify all postcodes where Hyperoptic currently has at least 50 residential subscribers (latest quarter)
                with hyperoptic_strongholds as (
                    select
                        postcode
                    from take_up_v3.report.rpt_postcode_lines_distribution_residential
                    where coalesce(hyperoptic_fttp, 0) >= 50
                ),
                -- Step 2: Get Hyperoptic's forecasted footprint in these postcodes at end of 2024 and end of 2027
                footprint_2024 as (
                    select postcode, present as present_2024
                    from forecast_v7.intermediate.int_forecast_output
                    where operator = 'Hyperoptic' and reported_at = '2024-06-01'
                ),
                footprint_2027 as (
                    select postcode, present as present_2027
                    from forecast_v7.intermediate.int_forecast_output
                    where operator = 'Hyperoptic' and reported_at = '2027-06-01'
                )
                -- Step 3: Join and calculate expansion
                select
                    hs.postcode,
                    coalesce(f24.present_2024, 0) as present_2024,
                    coalesce(f27.present_2027, 0) as present_2027
                from hyperoptic_strongholds hs
                left join footprint_2024 f24 on hs.postcode = f24.postcode
                left join footprint_2027 f27 on hs.postcode = f27.postcode
                -- Only interested in postcodes where there is a change or presence
                where coalesce(f24.present_2024, 0) <> coalesce(f27.present_2027, 0)
                or coalesce(f24.present_2024, 0) = 1
                or coalesce(f27.present_2027, 0) = 1
            """
        }
    ]
}