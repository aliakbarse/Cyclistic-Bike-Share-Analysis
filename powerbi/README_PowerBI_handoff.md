# Power BI Handoff

Everything up to the Power BI stage is done. This note lists what is ready and what is still open, so the dashboard can be built from a clear starting point.

## Ready

| Need | Source |
|---|---|
| Clean ride-level table (6,115,947 rows) | `03_Clean_Data/cyclistic_clean.csv` |
| Verified metric definitions (weekend, season, commute-like, duration buckets) | `05_SQL/04_final_queries.sql`, `06_Python/cyclistic_analysis.ipynb` |
| Reference values to check every dashboard measure against | `04_Excel/summary_tables.xlsx` |
| Story and recommendations | `09_Reports/Cyclistic_Findings_Report.md` |
| Colour convention used in analysis charts | Member = blue `#2a78d6`, Casual = orange `#eb6834` |

## Check values for dashboard measures

| Measure | Member | Casual |
|---|---|---|
| Total rides | 3,955,594 | 2,160,353 |
| Median ride (min) | 8.55 | 10.86 |
| Weekend share | 23.3% | 37.3% |
| Electric share | 68.1% | 73.6% |
| Summer share | 37.6% | 46.9% |
| Commute-like rides | 1,737,372 | 602,209 |

If a measure does not match, the model or DAX is wrong, not the data.

## Open decisions for the Power BI stage

1. Model shape: load the 6.1M-row table directly, or build a star schema (fact table plus date, hour, station, bike-type dimensions).
2. Which grain the visuals need (ride-level vs pre-aggregated).
3. Page layout: overview, timing and seasonality, stations, recommendations.
4. Whether median and percentile measures are computed in DAX or pre-computed.

The four placeholder files in `08_Visualizations/` (`dashboard_overview.png`, `member_vs_casual.png`, `usage_patterns.png`, `recommendations.png`) are reserved for dashboard exports.
