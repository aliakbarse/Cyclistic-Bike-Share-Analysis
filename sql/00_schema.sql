-- ============================================================
-- 00_schema.sql: table for the clean Cyclistic rides (PostgreSQL)
-- ============================================================
--
-- One row = one ride. This is the "grain" of the table: every
-- count, sum or average in the analysis starts from single rides.
--
-- The column order matches cyclistic_clean.csv exactly, because
-- the loader uses COPY, which maps CSV columns to table columns
-- by position.
--
-- Why these types:
--   * ride_id is TEXT and the PRIMARY KEY: PostgreSQL then refuses
--     a duplicate ride, so the 35 cross-file duplicates cannot come back.
--   * started_at / ended_at are TIMESTAMP (no time zone): the source
--     files give local Chicago time without an offset.
--   * latitude and longitude are DOUBLE PRECISION: 8 bytes, and no
--     rounding of the coordinates.
--   * CHECK constraints repeat the validation rules inside the
--     database, so bad data is rejected at load time.
-- ============================================================

DROP TABLE IF EXISTS cyclistic_clean;

CREATE TABLE cyclistic_clean (
    ride_id                 TEXT             PRIMARY KEY,
    rideable_type           TEXT             NOT NULL
        CHECK (rideable_type IN ('classic_bike', 'electric_bike')),
    started_at              TIMESTAMP        NOT NULL,
    ended_at                TIMESTAMP        NOT NULL,
    start_station_name      TEXT,
    start_station_id        TEXT,
    end_station_name        TEXT,
    end_station_id          TEXT,
    start_lat               DOUBLE PRECISION NOT NULL,
    start_lng               DOUBLE PRECISION NOT NULL,
    end_lat                 DOUBLE PRECISION,
    end_lng                 DOUBLE PRECISION,
    member_casual           TEXT             NOT NULL
        CHECK (member_casual IN ('casual', 'member')),
    source_file             TEXT             NOT NULL,
    ride_length_minutes_raw DOUBLE PRECISION NOT NULL,
    duration_dst_flag       SMALLINT         NOT NULL
        CHECK (duration_dst_flag IN (0, 1)),
    ride_length_minutes     DOUBLE PRECISION NOT NULL
        CHECK (ride_length_minutes >= 0),
    day_of_week             TEXT             NOT NULL,
    month                   TEXT             NOT NULL
);
