-- ============================================
-- CYCLISTIC DATA VALIDATION
-- ============================================

-- 1. Row count
SELECT COUNT(*) AS total_rows
FROM cyclistic_clean;


-- 2. Duplicate ride IDs
SELECT
    COUNT(*) - COUNT(DISTINCT ride_id) AS duplicate_rows
FROM cyclistic_clean;


-- 3. Rider categories
SELECT
    member_casual,
    COUNT(*) AS ride_count
FROM cyclistic_clean
GROUP BY member_casual
ORDER BY ride_count DESC;


-- 4. Bike types
SELECT
    rideable_type,
    COUNT(*) AS ride_count
FROM cyclistic_clean
GROUP BY rideable_type
ORDER BY ride_count DESC;


-- 5. Negative analytical durations
SELECT COUNT(*) AS negative_duration_rows
FROM cyclistic_clean
WHERE ride_length_minutes < 0;