-- ============================================================
-- CYCLISTIC BIKE-SHARE CASE STUDY
-- DEEP ANALYSIS
-- ============================================================
--
-- Database: cyclistic_db
-- Table: cyclistic_clean
--
-- Business question:
-- "How do annual members and casual riders use
--  Cyclistic bikes differently?"
--
-- Analysis workflow:
-- 01. Usage Windows by Rider Type
-- 02. Top Usage Windows
-- 03. Rider Type × Bike Type × Day Type
-- 04. Duration Distribution
-- 05. Casual Classic-Bike Weekend Usage Windows
-- 06. Casual Classic-Bike Weekend Duration Distribution
-- 07. Rider × Bike × Day × Duration
-- 08. Monthly Rider Mix
-- 09. Monthly Rider Behavior
-- 10. Seasonal Rider Behavior by Day Type
-- 11. Largest Casual Rider Segments
-- 12. Casual vs Member Segment Mix
-- 13. Rider Activity by Time Period
-- 14. Segment Opportunity Comparison
-- 15. Seasonal Opportunity Segment
-- 16. Opportunity Segment Duration Comparison
--
-- ============================================================


-- ============================================================
-- ANALYSIS 1: USAGE WINDOWS BY RIDER TYPE
-- ============================================================
--
-- Compare when casual riders and members start trips,
-- separating weekdays and weekends.
-- ============================================================

SELECT
    member_casual,

    CASE
        WHEN day_of_week IN ('Saturday', 'Sunday')
            THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,

    EXTRACT(HOUR FROM started_at)::INT AS start_hour,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (
            PARTITION BY member_casual
        ),
        2
    ) AS rider_share_pct

FROM cyclistic_clean

GROUP BY
    member_casual,
    day_type,
    start_hour

ORDER BY
    member_casual,
    day_type,
    start_hour;


-- ============================================================
-- ANALYSIS 2: TOP USAGE WINDOWS
-- ============================================================
--
-- Identify the five highest-volume usage windows for each
-- rider type.
-- ============================================================

WITH usage_windows AS (
    SELECT
        member_casual,

        CASE
            WHEN day_of_week IN ('Saturday', 'Sunday')
                THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type,

        EXTRACT(HOUR FROM started_at)::INT AS start_hour,

        COUNT(*) AS total_rides

    FROM cyclistic_clean

    GROUP BY
        member_casual,
        day_type,
        start_hour
),

ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY member_casual
            ORDER BY total_rides DESC
        ) AS rank

    FROM usage_windows
)

SELECT
    member_casual,
    day_type,
    start_hour,
    total_rides,
    rank

FROM ranked

WHERE rank <= 5

ORDER BY
    member_casual,
    rank;


-- ============================================================
-- ANALYSIS 3: RIDER TYPE × BIKE TYPE × DAY TYPE
-- ============================================================
--
-- Understand how rider type, bike type and weekday/weekend
-- behavior interact.
-- ============================================================

SELECT
    member_casual,
    rideable_type,

    CASE
        WHEN day_of_week IN ('Saturday', 'Sunday')
            THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (
            PARTITION BY member_casual
        ),
        2
    ) AS rider_share_pct,

    ROUND(
        AVG(ride_length_minutes)::numeric,
        2
    ) AS avg_duration_minutes

FROM cyclistic_clean

GROUP BY
    member_casual,
    rideable_type,
    day_type

ORDER BY
    member_casual,
    total_rides DESC;


-- ============================================================
-- ANALYSIS 4: DURATION DISTRIBUTION
-- ============================================================
--
-- Compare average, median and 75th-percentile trip duration.
--
-- Median and P75 are included because averages can be strongly
-- affected by unusually long rides.
-- ============================================================

SELECT
    member_casual,
    rideable_type,

    CASE
        WHEN day_of_week IN ('Saturday', 'Sunday')
            THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,

    COUNT(*) AS total_rides,

    ROUND(
        AVG(ride_length_minutes)::numeric,
        2
    ) AS avg_duration_minutes,

    ROUND(
        PERCENTILE_CONT(0.50)
        WITHIN GROUP (
            ORDER BY ride_length_minutes
        )::numeric,
        2
    ) AS median_duration_minutes,

    ROUND(
        PERCENTILE_CONT(0.75)
        WITHIN GROUP (
            ORDER BY ride_length_minutes
        )::numeric,
        2
    ) AS p75_duration_minutes

FROM cyclistic_clean

GROUP BY
    member_casual,
    rideable_type,
    day_type

ORDER BY
    member_casual,
    rideable_type,
    day_type;


-- ============================================================
-- ANALYSIS 5: CASUAL CLASSIC-BIKE WEEKEND USAGE WINDOWS
-- ============================================================
--
-- Investigate casual riders using classic bikes on weekends.
-- Average and median duration are included to identify whether
-- apparently long trips are driven by outliers.
-- ============================================================

SELECT
    EXTRACT(HOUR FROM started_at)::INT AS start_hour,

    COUNT(*) AS total_rides,

    ROUND(
        AVG(ride_length_minutes)::numeric,
        2
    ) AS avg_duration_minutes,

    ROUND(
        PERCENTILE_CONT(0.50)
        WITHIN GROUP (
            ORDER BY ride_length_minutes
        )::numeric,
        2
    ) AS median_duration_minutes

FROM cyclistic_clean

WHERE member_casual = 'casual'
  AND rideable_type = 'classic_bike'
  AND day_of_week IN ('Saturday', 'Sunday')

GROUP BY
    start_hour

ORDER BY
    total_rides DESC

LIMIT 10;


-- ============================================================
-- ANALYSIS 6: CASUAL CLASSIC-BIKE WEEKEND DURATION DISTRIBUTION
-- ============================================================
--
-- Determine whether long average trip durations among casual
-- classic-bike weekend rides represent typical trips or are
-- driven by a smaller number of long rides.
-- ============================================================

SELECT
    CASE
        WHEN ride_length_minutes < 15 THEN '<15 min'
        WHEN ride_length_minutes < 30 THEN '15–29 min'
        WHEN ride_length_minutes < 60 THEN '30–59 min'
        WHEN ride_length_minutes < 120 THEN '60–119 min'
        ELSE '120+ min'
    END AS duration_bucket,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS ride_share_pct

FROM cyclistic_clean

WHERE member_casual = 'casual'
  AND rideable_type = 'classic_bike'
  AND day_of_week IN ('Saturday', 'Sunday')

GROUP BY
    CASE
        WHEN ride_length_minutes < 15 THEN '<15 min'
        WHEN ride_length_minutes < 30 THEN '15–29 min'
        WHEN ride_length_minutes < 60 THEN '30–59 min'
        WHEN ride_length_minutes < 120 THEN '60–119 min'
        ELSE '120+ min'
    END

ORDER BY
    MIN(ride_length_minutes);


-- ============================================================
-- ANALYSIS 7: RIDER × BIKE × DAY × DURATION
-- ============================================================
--
-- Detailed behavioral segmentation using:
-- rider type, bike type, weekday/weekend and trip duration.
--
-- Rider share is calculated within each rider type.
-- ============================================================

SELECT
    member_casual,
    rideable_type,

    CASE
        WHEN day_of_week IN ('Saturday', 'Sunday')
            THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,

    CASE
        WHEN ride_length_minutes < 15 THEN '<15 min'
        WHEN ride_length_minutes < 30 THEN '15–29 min'
        WHEN ride_length_minutes < 60 THEN '30–59 min'
        ELSE '60+ min'
    END AS duration_bucket,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (
            PARTITION BY member_casual
        ),
        2
    ) AS rider_share_pct

FROM cyclistic_clean

GROUP BY
    member_casual,
    rideable_type,
    day_type,
    duration_bucket

ORDER BY
    member_casual,
    total_rides DESC;


-- ============================================================
-- ANALYSIS 8: MONTHLY RIDER MIX
-- ============================================================
--
-- Measure how the proportion of casual and member rides changes
-- from month to month.
--
-- source_file is used instead of the month column because it
-- represents the original monthly dataset and correctly handles
-- legitimate cross-month trips around dataset boundaries.
-- ============================================================

SELECT
    LEFT(source_file, 6) AS analysis_month,

    COUNT(*) FILTER (
        WHERE member_casual = 'casual'
    ) AS casual_rides,

    COUNT(*) FILTER (
        WHERE member_casual = 'member'
    ) AS member_rides,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) FILTER (
            WHERE member_casual = 'casual'
        ) * 100.0
        / COUNT(*),
        2
    ) AS casual_share_pct

FROM cyclistic_clean

GROUP BY
    LEFT(source_file, 6)

ORDER BY
    analysis_month;


-- ============================================================
-- ANALYSIS 9: MONTHLY RIDER BEHAVIOR
-- ============================================================
--
-- Compare monthly ride volume, average duration, median duration
-- and electric-bike share for casual riders and members.
-- ============================================================

SELECT
    LEFT(source_file, 6) AS analysis_month,

    member_casual,

    COUNT(*) AS total_rides,

    ROUND(
        AVG(ride_length_minutes)::numeric,
        2
    ) AS avg_duration_minutes,

    ROUND(
        PERCENTILE_CONT(0.50)
        WITHIN GROUP (
            ORDER BY ride_length_minutes
        )::numeric,
        2
    ) AS median_duration_minutes,

    ROUND(
        COUNT(*) FILTER (
            WHERE rideable_type = 'electric_bike'
        ) * 100.0
        / COUNT(*),
        2
    ) AS electric_share_pct

FROM cyclistic_clean

GROUP BY
    LEFT(source_file, 6),
    member_casual

ORDER BY
    analysis_month,
    member_casual;


-- ============================================================
-- ANALYSIS 10: SEASONAL RIDER BEHAVIOR BY DAY TYPE
-- ============================================================
--
-- Understand how weekday/weekend behavior changes across the
-- year for each rider type.
-- ============================================================

SELECT
    LEFT(source_file, 6) AS analysis_month,

    member_casual,

    CASE
        WHEN day_of_week IN ('Saturday', 'Sunday')
            THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (
            PARTITION BY
                LEFT(source_file, 6),
                member_casual
        ),
        2
    ) AS monthly_rider_share_pct,

    ROUND(
        AVG(ride_length_minutes)::numeric,
        2
    ) AS avg_duration_minutes

FROM cyclistic_clean

GROUP BY
    LEFT(source_file, 6),
    member_casual,
    day_type

ORDER BY
    analysis_month,
    member_casual,
    day_type;


-- ============================================================
-- ANALYSIS 11: LARGEST CASUAL RIDER SEGMENTS
-- ============================================================
--
-- Identify the largest behavioral segments within the casual
-- rider population.
-- ============================================================

SELECT
    rideable_type,

    CASE
        WHEN day_of_week IN ('Saturday', 'Sunday')
            THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,

    CASE
        WHEN ride_length_minutes < 15 THEN '<15 min'
        WHEN ride_length_minutes < 30 THEN '15–29 min'
        WHEN ride_length_minutes < 60 THEN '30–59 min'
        ELSE '60+ min'
    END AS duration_bucket,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS casual_share_pct

FROM cyclistic_clean

WHERE member_casual = 'casual'

GROUP BY
    rideable_type,
    day_type,
    duration_bucket

ORDER BY
    total_rides DESC;


-- ============================================================
-- ANALYSIS 12: CASUAL VS MEMBER SEGMENT MIX
-- ============================================================
--
-- Compare the behavioral composition of casual riders and
-- members using the same segmentation framework.
--
-- This identifies behavioral overlap. It does NOT prove that
-- a casual rider is likely to become a member because the
-- dataset contains no individual customer ID, conversion data,
-- pricing data or membership-campaign data.
-- ============================================================

SELECT
    member_casual,
    rideable_type,

    CASE
        WHEN day_of_week IN ('Saturday', 'Sunday')
            THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,

    CASE
        WHEN ride_length_minutes < 15 THEN '<15 min'
        WHEN ride_length_minutes < 30 THEN '15–29 min'
        WHEN ride_length_minutes < 60 THEN '30–59 min'
        ELSE '60+ min'
    END AS duration_bucket,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (
            PARTITION BY member_casual
        ),
        2
    ) AS rider_share_pct

FROM cyclistic_clean

GROUP BY
    member_casual,
    rideable_type,
    day_type,
    duration_bucket

ORDER BY
    member_casual,
    total_rides DESC;


-- ============================================================
-- ANALYSIS 13: RIDER ACTIVITY BY TIME PERIOD
-- ============================================================
--
-- Compare broad daily activity periods between casual riders
-- and members.
--
-- These are activity periods, not inferred trip purposes.
-- Morning activity should not automatically be interpreted as
-- commuting because trip-purpose data is absent.
-- ============================================================

SELECT
    member_casual,

    CASE
        WHEN EXTRACT(HOUR FROM started_at) BETWEEN 6 AND 9
            THEN 'Morning peak (06–09)'

        WHEN EXTRACT(HOUR FROM started_at) BETWEEN 10 AND 15
            THEN 'Midday (10–15)'

        WHEN EXTRACT(HOUR FROM started_at) BETWEEN 16 AND 19
            THEN 'Afternoon/evening peak (16–19)'

        ELSE 'Other hours'
    END AS time_period,

    COUNT(*) AS total_rides,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (
            PARTITION BY member_casual
        ),
        2
    ) AS rider_share_pct

FROM cyclistic_clean

GROUP BY
    member_casual,
    time_period

ORDER BY
    member_casual,
    total_rides DESC;


-- ============================================================
-- ANALYSIS 14: SEGMENT OPPORTUNITY COMPARISON
-- ============================================================
--
-- Identify behavioral segments where casual riders have
-- substantial ride volume and compare their representation
-- with members.
--
-- This is a behavioral opportunity analysis, NOT a prediction
-- of actual membership conversion.
-- ============================================================

WITH segment_data AS (
    SELECT
        rideable_type,

        CASE
            WHEN day_of_week IN ('Saturday', 'Sunday')
                THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type,

        CASE
            WHEN ride_length_minutes < 15 THEN '<15 min'
            WHEN ride_length_minutes < 30 THEN '15–29 min'
            WHEN ride_length_minutes < 60 THEN '30–59 min'
            ELSE '60+ min'
        END AS duration_bucket,

        member_casual,

        COUNT(*) AS total_rides

    FROM cyclistic_clean

    GROUP BY
        rideable_type,
        day_type,
        duration_bucket,
        member_casual
),

segment_comparison AS (
    SELECT
        rideable_type,
        day_type,
        duration_bucket,

        SUM(
            CASE
                WHEN member_casual = 'casual'
                    THEN total_rides
                ELSE 0
            END
        ) AS casual_rides,

        SUM(
            CASE
                WHEN member_casual = 'member'
                    THEN total_rides
                ELSE 0
            END
        ) AS member_rides

    FROM segment_data

    GROUP BY
        rideable_type,
        day_type,
        duration_bucket
)

SELECT
    rideable_type,
    day_type,
    duration_bucket,

    casual_rides,
    member_rides,

    ROUND(
        casual_rides * 100.0
        / SUM(casual_rides) OVER (),
        2
    ) AS casual_share_pct,

    ROUND(
        member_rides * 100.0
        / SUM(member_rides) OVER (),
        2
    ) AS member_share_pct,

    ROUND(
        (
            casual_rides * 100.0
            / SUM(casual_rides) OVER ()
        )
        -
        (
            member_rides * 100.0
            / SUM(member_rides) OVER ()
        ),
        2
    ) AS casual_vs_member_share_gap_pp

FROM segment_comparison

ORDER BY
    casual_rides DESC;


-- ============================================================
-- ANALYSIS 15: SEASONAL OPPORTUNITY SEGMENT
-- ============================================================
--
-- Focus:
--   Casual rider
--   Electric bike
--   Weekend
--   Under 30 minutes
--
-- Identify when this behavioral opportunity is most
-- concentrated throughout the year.
-- ============================================================

WITH monthly_data AS (
    SELECT
        LEFT(source_file, 6) AS analysis_month,

        COUNT(*) AS opportunity_rides

    FROM cyclistic_clean

    WHERE member_casual = 'casual'
      AND rideable_type = 'electric_bike'
      AND day_of_week IN ('Saturday', 'Sunday')
      AND ride_length_minutes < 30

    GROUP BY
        LEFT(source_file, 6)
),

monthly_totals AS (
    SELECT
        LEFT(source_file, 6) AS analysis_month,

        COUNT(*) AS total_rides,

        COUNT(*) FILTER (
            WHERE member_casual = 'casual'
        ) AS total_casual_rides

    FROM cyclistic_clean

    GROUP BY
        LEFT(source_file, 6)
)

SELECT
    m.analysis_month,

    m.opportunity_rides,

    t.total_rides,

    t.total_casual_rides,

    ROUND(
        m.opportunity_rides * 100.0
        / t.total_rides,
        2
    ) AS share_of_all_monthly_rides_pct,

    ROUND(
        m.opportunity_rides * 100.0
        / t.total_casual_rides,
        2
    ) AS share_of_monthly_casual_rides_pct

FROM monthly_data m

JOIN monthly_totals t
    ON m.analysis_month = t.analysis_month

ORDER BY
    m.analysis_month;


-- ============================================================
-- ANALYSIS 16: OPPORTUNITY SEGMENT DURATION COMPARISON
-- ============================================================
--
-- Compare duration behavior between casual riders and members
-- within the same high-opportunity segment:
--
--   Electric bike
--   Weekend
--   Under 30 minutes
--
-- This tests whether the opportunity differs in both volume
-- and trip duration.
-- ============================================================

SELECT
    member_casual,

    COUNT(*) AS total_rides,

    ROUND(
        AVG(ride_length_minutes)::numeric,
        2
    ) AS avg_duration_minutes,

    ROUND(
        PERCENTILE_CONT(0.50)
        WITHIN GROUP (
            ORDER BY ride_length_minutes
        )::numeric,
        2
    ) AS median_duration_minutes,

    ROUND(
        PERCENTILE_CONT(0.75)
        WITHIN GROUP (
            ORDER BY ride_length_minutes
        )::numeric,
        2
    ) AS p75_duration_minutes

FROM cyclistic_clean

WHERE rideable_type = 'electric_bike'
  AND day_of_week IN ('Saturday', 'Sunday')
  AND ride_length_minutes < 30

GROUP BY
    member_casual

ORDER BY
    member_casual;


-- ============================================================
-- END OF DEEP ANALYSIS
-- ============================================================