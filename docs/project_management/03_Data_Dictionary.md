# Data Dictionary

## Dataset Overview

Source: Cyclistic bike-share trip data
Period: September 2025 – August 2026
Number of monthly files: 12
Total records: 6,115,982
Number of columns: 13

## Fields

| Column | Data Type | Description | Analytical Role | Important Notes |
|---|---|---|---|---|
| `ride_id` | String | Unique identifier assigned to a bike ride | Counting rides, identifying unique rides, duplicate detection | 35 ride IDs were found duplicated across monthly files and will be handled during PROCESS |
| `rideable_type` | String | Type of bike used for the ride | Compare usage and preferences by bike type | Values are `classic_bike` and `electric_bike`; bike availability is not directly measured in the dataset |
| `started_at` | Datetime | Date and time when the ride started | Analyze usage by hour, day, weekday, month, and season | Required for time-based analysis and ride-duration calculation |
| `ended_at` | Datetime | Date and time when the ride ended | Calculate ride duration and analyze ending times | Used together with `started_at`; 29 negative-duration records were identified and linked to the DST clock change |
| `start_station_name` | String | Name of the station where the ride started | Identify popular starting locations and analyze station usage | Missing for a substantial share of rides, particularly electric-bike trips |
| `start_station_id` | String | Identifier of the starting station | Identify and group station-level records | Can provide a more stable station identifier than station name |
| `end_station_name` | String | Name of the station where the ride ended | Identify popular destinations and destination patterns | Missing for a substantial share of rides, particularly electric-bike trips |
| `end_station_id` | String | Identifier of the ending station | Analyze destinations and station-to-station routes | Useful for grouping destination records and route analysis |
| `start_lat` | Numeric | Latitude of the ride starting location | Geographic analysis and mapping of starting points | No missing or technically invalid values were found |
| `start_lng` | Numeric | Longitude of the ride starting location | Geographic analysis and mapping of starting points | No missing or technically invalid values were found |
| `end_lat` | Numeric | Latitude of the ride ending location | Geographic analysis and mapping of destinations | 5,426 values (0.0887%) are missing |
| `end_lng` | Numeric | Longitude of the ride ending location | Geographic analysis and mapping of destinations | 5,426 values (0.0887%) are missing |
| `member_casual` | String | Indicates whether the rider is an annual member or casual rider | Primary segmentation variable for comparing rider behavior | Values are `member` and `casual`; no missing or unexpected values were found |

## Derived Variables

Variables that will be created during the PROCESS phase:

| Variable | Definition | Purpose |
|---|---|---|
| `ride_length` | Difference between `ended_at` and `started_at` | Measure how long each ride lasted |
| `day_of_week` | Day derived from `started_at` | Compare usage across weekdays |
| `month` | Month derived from `started_at` | Analyze monthly and seasonal patterns |