-- ============================================
-- 1. RIDER TYPE OVERVIEW
-- ============================================

SELECT
    member_casual,
    COUNT(*) AS total_rides,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS ride_share_pct
FROM cyclistic_clean
GROUP BY member_casual
ORDER BY total_rides DESC;

-- ============================================
-- 2. RIDE DURATION BY RIDER TYPE
-- ============================================

SELECT
    member_casual,
    COUNT(*) AS total_rides,
    ROUND(AVG(ride_length_minutes)::numeric, 2) AS avg_duration_minutes,
    ROUND(
        PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY ride_length_minutes)::numeric,
        2
    ) AS median_duration_minutes
FROM cyclistic_clean
GROUP BY member_casual
ORDER BY avg_duration_minutes DESC;

-- ============================================
-- 3. RIDES BY DAY OF WEEK AND RIDER TYPE
-- ============================================

SELECT
    member_casual,
    day_of_week,
    COUNT(*) AS total_rides,
    ROUND(AVG(ride_length_minutes)::numeric, 2) AS avg_duration_minutes
FROM cyclistic_clean
GROUP BY
    member_casual,
    day_of_week
ORDER BY
    member_casual,
    total_rides DESC;

-- ============================================
-- 4. WEEKDAY VS WEEKEND BEHAVIOR
-- ============================================

SELECT
    member_casual,
    CASE
        WHEN day_of_week IN ('Saturday', 'Sunday')
            THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(*) AS total_rides,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (PARTITION BY member_casual),
        2
    ) AS ride_share_pct,
    ROUND(AVG(ride_length_minutes)::numeric, 2)
        AS avg_duration_minutes
FROM cyclistic_clean
GROUP BY
    member_casual,
    day_type
ORDER BY
    member_casual,
    day_type; 

-- ============================================
-- 5. RIDES BY HOUR OF DAY
-- ============================================

SELECT
    member_casual,
    EXTRACT(HOUR FROM started_at)::INT AS start_hour,
    COUNT(*) AS total_rides,
    ROUND(AVG(ride_length_minutes)::numeric, 2)
        AS avg_duration_minutes
FROM cyclistic_clean
GROUP BY
    member_casual,
    start_hour
ORDER BY
    member_casual,
    start_hour;

-- ============================================
-- 6. HOURLY USAGE PROFILE BY RIDER TYPE
-- ============================================

SELECT
    member_casual,
    EXTRACT(HOUR FROM started_at)::INT AS start_hour,
    COUNT(*) AS total_rides,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (PARTITION BY member_casual),
        2
    ) AS rider_hour_share_pct
FROM cyclistic_clean
GROUP BY
    member_casual,
    start_hour
ORDER BY
    member_casual,
    start_hour;

-- ============================================
-- 7. BIKE TYPE PREFERENCE BY RIDER TYPE
-- ============================================

SELECT
    member_casual,
    rideable_type,
    COUNT(*) AS total_rides,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (PARTITION BY member_casual),
        2
    ) AS rider_bike_share_pct
FROM cyclistic_clean
GROUP BY
    member_casual,
    rideable_type
ORDER BY
    member_casual,
    total_rides DESC;

-- ============================================
-- 8. MONTHLY RIDER BEHAVIOR
-- ============================================

SELECT
    member_casual,
    LEFT(source_file, 6) AS analysis_month,
    COUNT(*) AS total_rides,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (PARTITION BY member_casual),
        2
    ) AS rider_month_share_pct,
    ROUND(AVG(ride_length_minutes)::numeric, 2)
        AS avg_duration_minutes
FROM cyclistic_clean
GROUP BY
    member_casual,
    LEFT(source_file, 6)
ORDER BY
    member_casual,
    analysis_month;

-- ============================================
-- 9. RIDER MIX BY MONTH
-- ============================================

SELECT
    LEFT(source_file, 6) AS analysis_month,
    COUNT(*) FILTER (WHERE member_casual = 'casual') AS casual_rides,
    COUNT(*) FILTER (WHERE member_casual = 'member') AS member_rides,
    COUNT(*) AS total_rides,
    ROUND(
        COUNT(*) FILTER (WHERE member_casual = 'casual') * 100.0
        / COUNT(*),
        2
    ) AS casual_share_pct
FROM cyclistic_clean
GROUP BY LEFT(source_file, 6)
ORDER BY analysis_month;