# PROCESS — Cleaning Plan

## Objective

Prepare a reproducible analytical dataset for answering:

> How do annual members and casual riders use Cyclistic bikes differently?

## Data Handling Principles

### Rule 1 — Preserve Raw Data

The original raw files will not be modified.

### Rule 2 — Reproducibility

All cleaning and transformation steps will be performed through documented, reproducible procedures.

## Cleaning Rules

| Issue | Evidence | Decision | Reason |
|---|---|---|---|
| Duplicate ride IDs | 35 exact duplicate ride IDs across April and May 2026 | Deduplicate by `ride_id`; retain the record associated with the `ended_at` month | Prevents double-counting while using a deterministic rule |
| Missing station information | Substantial station-level missingness, especially for electric-bike trips | Retain rides in the master dataset; exclude missing station IDs only from station-specific analyses | Prevents unnecessary loss of otherwise valid rides |
| Missing end coordinates | 5,426 records (0.0887%) | Retain records; exclude only from analyses requiring complete end coordinates | Missing destination coordinates do not invalidate the ride itself |
| Negative ride durations | 29 records around the DST transition | Retain records, flag DST-affected rows, and create an adjusted analytical duration | Preserves legitimate rides while preventing negative durations from distorting duration analysis |
| Invalid categorical values | None found | No transformation required | All observed values are valid and complete |
| Invalid coordinates | None found | No transformation required | All available coordinates are technically valid and geographically plausible |
| Timestamp issues | Initial validation found no invalid timestamp rows; DST ambiguity identified | Parse timestamps explicitly, detect invalid values, preserve legitimate cross-midnight rides, and flag DST-related cases | Ensures reliable time and duration calculations |

## Derived Variables

| Variable | Definition | Purpose |
|---|---|---|
| `ride_length_minutes_raw` | Difference between `ended_at` and `started_at` in minutes before special handling | Preserve the original calculated duration |
| `duration_dst_flag` | Indicator for records affected by the DST-related negative-duration issue | Make special-duration treatment traceable |
| `ride_length_minutes` | Analytical ride duration after documented DST treatment | Main duration metric |
| `day_of_week` | Day derived from `started_at` | Compare usage across weekdays |
| `month` | Month derived from `started_at` | Analyze monthly and seasonal patterns |

## Verification Plan

After cleaning, verify:

- Row count
- Unique ride IDs
- Membership values
- Bike-type values
- Missing values
- Ride-duration validity
- Coordinate validity
- Date range
- DST-flagged records
- Duplicate ride IDs

## Output

Clean analytical dataset: