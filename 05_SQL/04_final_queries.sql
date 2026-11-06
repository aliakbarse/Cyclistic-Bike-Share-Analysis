-- ============================================================
-- CYCLISTIC BIKE-SHARE CASE STUDY
-- FINAL QUERIES (SHARE-READY TABLES)
-- ============================================================
--
-- Database: cyclistic_db (PostgreSQL)
-- Table:    cyclistic_clean
--
-- Business task:
-- Identify how annual members and casual riders use Cyclistic
-- bikes differently, and what that implies for converting
-- casual riders into annual members.
--
-- This file complements 03_analysis.sql. It adds the tables the
-- final report needs that the deep analysis did not cover:
--
-- F01. Headline KPIs by rider type
-- F02. Weekday x hour heatmap table
-- F03. Seasonal behaviour by rider type
-- F04. Commute-like casual rides (members' core pattern)
-- F05. Round trips (same start and end station)
-- F06. Top start stations for casual riders
-- F07. Stations with the highest casual share
-- F08. Station-data coverage (limitation disclosure)
-- F09. Duration outliers and sensitivity check
--
-- Conventions
-- -----------
-- * Month / season use LEFT(source_file, 6), consistent with
--   03_analysis.sql (handles rides that cross month boundaries).
-- * Weekend = Saturday, Sunday.
-- * Commute-like window = weekday AND start hour in 06-09 or
--   16-19 (same windows as Analysis 13).
-- * ::numeric casts are required for ROUND() in PostgreSQL when
--   the input is double precision.
-- ============================================================


-- ============================================================
-- F01: HEADLINE KPIs BY RIDER TYPE
-- ============================================================
--
-- One row per rider type: volume, duration distribution,
-- weekend and electric-bike share. Median and P90 are reported
-- next to the mean because the mean is pulled up by a small
-- number of very long rides (see F09).
-- ============================================================

SELECT
    member_casual,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS ride_share_pct,

    ROUND(AVG(ride_length_minutes)::numeric, 2)
        AS avg_duration_minutes,

    ROUND(
        PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY ride_length_minutes)::numeric,
        2
    ) AS median_duration_minutes,

    ROUND(
        PERCENTILE_CONT(0.90)
        WITHIN GROUP (ORDER BY ride_length_minutes)::numeric,
        2
    ) AS p90_duration_minutes,

    ROUND(
        SUM(ride_length_minutes)::numeric / 60.0,
        0
    ) AS total_ride_hours,

    ROUND(
        COUNT(*) FILTER (
            WHERE day_of_week IN ('Saturday', 'Sunday')
        ) * 100.0 / COUNT(*),
        2
    ) AS weekend_share_pct,

    ROUND(
        COUNT(*) FILTER (
            WHERE rideable_type = 'electric_bike'
        ) * 100.0 / COUNT(*),
        2
    ) AS electric_share_pct

FROM cyclistic_clean

GROUP BY member_casual

ORDER BY member_casual;


-- ============================================================
-- F02: WEEKDAY x HOUR HEATMAP TABLE
-- ============================================================
--
-- Ride counts for every weekday/hour cell, by rider type, and
-- each cell as a share of that rider type's rides. Feeds the
-- heatmap that contrasts members' commute peaks with casual
-- riders' midday and weekend usage.
-- ============================================================

SELECT
    member_casual,

    CASE day_of_week
        WHEN 'Monday'    THEN 1
        WHEN 'Tuesday'   THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday'  THEN 4
        WHEN 'Friday'    THEN 5
        WHEN 'Saturday'  THEN 6
        WHEN 'Sunday'    THEN 7
    END AS day_number,

    day_of_week,

    EXTRACT(HOUR FROM started_at)::INT AS start_hour,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (PARTITION BY member_casual),
        3
    ) AS rider_share_pct

FROM cyclistic_clean

GROUP BY
    member_casual,
    day_number,
    day_of_week,
    start_hour

ORDER BY
    member_casual,
    day_number,
    start_hour;


-- ============================================================
-- F03: SEASONAL BEHAVIOUR BY RIDER TYPE
-- ============================================================
--
-- Season is derived from the dataset month:
--   Autumn = Sep-Nov, Winter = Dec-Feb,
--   Spring = Mar-May, Summer = Jun-Aug.
--
-- Shows (a) how much of each rider type's annual volume falls
-- in each season and (b) the casual share of all rides within
-- each season.
-- ============================================================

WITH seasonal AS (
    SELECT
        member_casual,

        CASE SUBSTR(source_file, 5, 2)
            WHEN '12' THEN 'Winter'
            WHEN '01' THEN 'Winter'
            WHEN '02' THEN 'Winter'
            WHEN '03' THEN 'Spring'
            WHEN '04' THEN 'Spring'
            WHEN '05' THEN 'Spring'
            WHEN '06' THEN 'Summer'
            WHEN '07' THEN 'Summer'
            WHEN '08' THEN 'Summer'
            ELSE 'Autumn'
        END AS season,

        ride_length_minutes

    FROM cyclistic_clean
)

SELECT
    season,
    member_casual,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (PARTITION BY member_casual),
        2
    ) AS rider_annual_share_pct,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (PARTITION BY season),
        2
    ) AS rider_share_of_season_pct,

    ROUND(AVG(ride_length_minutes)::numeric, 2)
        AS avg_duration_minutes,

    ROUND(
        PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY ride_length_minutes)::numeric,
        2
    ) AS median_duration_minutes

FROM seasonal

GROUP BY
    season,
    member_casual

ORDER BY
    CASE season
        WHEN 'Spring' THEN 1
        WHEN 'Summer' THEN 2
        WHEN 'Autumn' THEN 3
        ELSE 4
    END,
    member_casual;


-- ============================================================
-- F04: COMMUTE-LIKE RIDES BY RIDER TYPE
-- ============================================================
--
-- Members' defining pattern is weekday rides in the morning and
-- late-afternoon windows. This query measures how many casual
-- rides look the same (weekday, commute window, under 30 min).
--
-- IMPORTANT: this describes ride behaviour only. Without trip
-- purpose or rider IDs it does not prove these are commuters or
-- that they would convert to membership.
-- ============================================================

SELECT
    member_casual,

    COUNT(*) AS total_rides,

    COUNT(*) FILTER (
        WHERE day_of_week NOT IN ('Saturday', 'Sunday')
          AND (
                EXTRACT(HOUR FROM started_at) BETWEEN 6 AND 9
             OR EXTRACT(HOUR FROM started_at) BETWEEN 16 AND 19
          )
    ) AS weekday_commute_window_rides,

    COUNT(*) FILTER (
        WHERE day_of_week NOT IN ('Saturday', 'Sunday')
          AND (
                EXTRACT(HOUR FROM started_at) BETWEEN 6 AND 9
             OR EXTRACT(HOUR FROM started_at) BETWEEN 16 AND 19
          )
          AND ride_length_minutes < 30
    ) AS commute_like_rides,

    ROUND(
        COUNT(*) FILTER (
            WHERE day_of_week NOT IN ('Saturday', 'Sunday')
              AND (
                    EXTRACT(HOUR FROM started_at) BETWEEN 6 AND 9
                 OR EXTRACT(HOUR FROM started_at) BETWEEN 16 AND 19
              )
              AND ride_length_minutes < 30
        ) * 100.0 / COUNT(*),
        2
    ) AS commute_like_share_pct

FROM cyclistic_clean

GROUP BY member_casual

ORDER BY member_casual;


-- ============================================================
-- F05: ROUND TRIPS (SAME START AND END STATION)
-- ============================================================
--
-- A round trip starts and ends at the same station. This is a
-- common leisure/sightseeing signal (a bike is taken out and
-- brought back) versus A-to-B transport.
--
-- Only rides with BOTH station IDs are used, so the result is
-- driven mainly by classic bikes and docked e-bike trips.
-- Station-less electric rides are excluded (see F08).
-- ============================================================

SELECT
    member_casual,
    rideable_type,

    COUNT(*) AS rides_with_both_stations,

    COUNT(*) FILTER (
        WHERE start_station_id = end_station_id
    ) AS round_trips,

    ROUND(
        COUNT(*) FILTER (
            WHERE start_station_id = end_station_id
        ) * 100.0 / COUNT(*),
        2
    ) AS round_trip_pct,

    ROUND(
        AVG(ride_length_minutes) FILTER (
            WHERE start_station_id = end_station_id
        )::numeric,
        2
    ) AS avg_round_trip_minutes

FROM cyclistic_clean

WHERE start_station_id IS NOT NULL
  AND end_station_id   IS NOT NULL

GROUP BY
    member_casual,
    rideable_type

ORDER BY
    member_casual,
    rideable_type;


-- ============================================================
-- F06: TOP 15 START STATIONS FOR CASUAL RIDERS
-- ============================================================
--
-- Where casual riders start most often. Useful for deciding
-- where in-station and geo-targeted digital promotion would
-- reach the most casual riders.
--
-- Only rides with a start station ID are included.
-- ============================================================

SELECT
    start_station_id,

    MIN(start_station_name) AS start_station_name,

    ROUND(AVG(start_lat)::numeric, 5) AS avg_lat,
    ROUND(AVG(start_lng)::numeric, 5) AS avg_lng,

    COUNT(*) FILTER (WHERE member_casual = 'casual')
        AS casual_rides,

    COUNT(*) FILTER (WHERE member_casual = 'member')
        AS member_rides,

    ROUND(
        COUNT(*) FILTER (WHERE member_casual = 'casual')
        * 100.0 / COUNT(*),
        2
    ) AS casual_share_pct

FROM cyclistic_clean

WHERE start_station_id IS NOT NULL

GROUP BY start_station_id

ORDER BY casual_rides DESC

LIMIT 15;


-- ============================================================
-- F07: STATIONS WITH THE HIGHEST CASUAL SHARE
-- ============================================================
--
-- Stations where casual riders make up the largest share of
-- rides. A minimum of 5,000 rides filters out low-volume
-- stations whose shares are unstable.
-- ============================================================

SELECT
    start_station_id,

    MIN(start_station_name) AS start_station_name,

    COUNT(*) AS total_rides,

    COUNT(*) FILTER (WHERE member_casual = 'casual')
        AS casual_rides,

    ROUND(
        COUNT(*) FILTER (WHERE member_casual = 'casual')
        * 100.0 / COUNT(*),
        2
    ) AS casual_share_pct

FROM cyclistic_clean

WHERE start_station_id IS NOT NULL

GROUP BY start_station_id

HAVING COUNT(*) >= 5000

ORDER BY casual_share_pct DESC

LIMIT 15;


-- ============================================================
-- F08: STATION-DATA COVERAGE (LIMITATION DISCLOSURE)
-- ============================================================
--
-- Share of rides with a start station, by rider type and bike
-- type. Quantifies how much of the data F05-F07 can see.
-- ============================================================

SELECT
    member_casual,
    rideable_type,

    COUNT(*) AS total_rides,

    COUNT(*) FILTER (WHERE start_station_id IS NOT NULL)
        AS rides_with_start_station,

    ROUND(
        COUNT(*) FILTER (WHERE start_station_id IS NOT NULL)
        * 100.0 / COUNT(*),
        2
    ) AS start_station_coverage_pct

FROM cyclistic_clean

GROUP BY
    member_casual,
    rideable_type

ORDER BY
    member_casual,
    rideable_type;


-- ============================================================
-- F09: DURATION OUTLIERS AND SENSITIVITY CHECK
-- ============================================================
--
-- The cleaning plan retains every ride. This query measures how
-- sensitive the headline duration comparison is to the shortest
-- (under 1 minute: false starts / immediate returns) and the
-- longest (over 3 hours) rides.
-- ============================================================

SELECT
    member_casual,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) FILTER (WHERE ride_length_minutes < 1)
        * 100.0 / COUNT(*),
        2
    ) AS under_1_min_pct,

    ROUND(
        COUNT(*) FILTER (WHERE ride_length_minutes >= 180)
        * 100.0 / COUNT(*),
        2
    ) AS over_3_hours_pct,

    ROUND(AVG(ride_length_minutes)::numeric, 2)
        AS avg_all_rides_minutes,

    ROUND(
        AVG(ride_length_minutes) FILTER (
            WHERE ride_length_minutes >= 1
              AND ride_length_minutes < 180
        )::numeric,
        2
    ) AS avg_trimmed_1_to_180_minutes,

    ROUND(
        PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY ride_length_minutes)::numeric,
        2
    ) AS median_all_rides_minutes

FROM cyclistic_clean

GROUP BY member_casual

ORDER BY member_casual;


-- ============================================================
-- END OF FINAL QUERIES
-- ============================================================
