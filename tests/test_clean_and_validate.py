"""Tests for the cleaning rules and the validation checks.

Each test builds a tiny trip table (a few rows) and checks one rule:
- a ride id found in two monthly files is kept only in the file of the
  month the ride ended, so it is counted once;
- a negative duration on the daylight-saving date is flagged and corrected
  by one hour, and the raw duration is kept;
- a negative duration on any other date is not silently corrected, so the
  validation catches it;
- day_of_week, month and source_file are added correctly;
- validation fails on duplicate ids (also inside one chunk), invalid
  category values and a wrong row count.

The last test runs the real 6.1 million row file. It is skipped unless the
clean file exists and CYCLISTIC_FULL_TESTS=1 is set.

Run with: python -m pytest -v
"""

import os

import pandas as pd
import pytest

from cyclistic import config
from cyclistic.clean import clean_all, clean_month
from cyclistic.validate import validate_chunks, validate_file


def make_trips(rows):
    """rows: list of (ride_id, started_at, ended_at)."""
    return pd.DataFrame(
        {
            "ride_id": [r[0] for r in rows],
            "rideable_type": "classic_bike",
            "started_at": [r[1] for r in rows],
            "ended_at": [r[2] for r in rows],
            "start_station_name": "A",
            "start_station_id": "1",
            "end_station_name": "B",
            "end_station_id": "2",
            "start_lat": 41.9,
            "start_lng": -87.6,
            "end_lat": 41.9,
            "end_lng": -87.6,
            "member_casual": "member",
        }
    )


def test_duplicate_kept_only_in_end_month_file():
    # DUP starts on 30 April and ends on 1 May: it appears in both files.
    row = ("DUP", "2026-04-30 23:50:00", "2026-05-01 00:10:00")
    april = make_trips([row, ("A1", "2026-04-10 10:00:00", "2026-04-10 10:20:00")])
    may = make_trips([row])

    april_clean = clean_month(april, "202604-tripdata.csv", {"DUP"})
    may_clean = clean_month(may, "202605-tripdata.csv", {"DUP"})
    combined = pd.concat([april_clean, may_clean], ignore_index=True)

    assert list(april_clean["ride_id"]) == ["A1"]
    assert list(may_clean["ride_id"]) == ["DUP"]
    assert combined["ride_id"].is_unique


def test_ride_not_in_duplicate_list_is_never_removed():
    df = make_trips([("X", "2026-04-30 23:50:00", "2026-05-01 00:10:00")])
    out = clean_month(df, "202604-tripdata.csv", set())
    assert len(out) == 1


def test_dst_negative_duration_is_flagged_and_corrected():
    df = make_trips([("D", "2025-11-02 01:30:00", "2025-11-02 01:10:00")])
    out = clean_month(df, "202511-tripdata.csv", set()).iloc[0]

    assert out["ride_length_minutes_raw"] == pytest.approx(-20)
    assert out["duration_dst_flag"] == 1
    assert out["ride_length_minutes"] == pytest.approx(40)


def test_normal_ride_is_not_flagged():
    df = make_trips([("N", "2025-11-02 09:00:00", "2025-11-02 09:30:00")])
    out = clean_month(df, "202511-tripdata.csv", set()).iloc[0]

    assert out["duration_dst_flag"] == 0
    assert out["ride_length_minutes"] == pytest.approx(30)
    assert out["ride_length_minutes"] == out["ride_length_minutes_raw"]


def test_negative_duration_on_other_date_is_not_hidden():
    df = make_trips([("B", "2025-12-05 10:30:00", "2025-12-05 10:10:00")])
    out = clean_month(df, "202512-tripdata.csv", set())
    assert out.iloc[0]["duration_dst_flag"] == 0
    assert out.iloc[0]["ride_length_minutes"] < 0
    result = validate_chunks([out])
    assert result["checks"]["no_negative_durations"] is False


def test_derived_columns():
    df = make_trips([("T", "2026-03-07 08:00:00", "2026-03-07 08:15:00")])
    out = clean_month(df, "202603-tripdata.csv", set()).iloc[0]

    assert out["day_of_week"] == "Saturday"
    assert out["month"] == "2026-03"
    assert out["source_file"] == "202603-tripdata.csv"


def test_clean_month_does_not_change_its_input():
    df = make_trips([("T", "2026-03-07 08:00:00", "2026-03-07 08:15:00")])
    before = df.copy()
    clean_month(df, "202603-tripdata.csv", set())
    pd.testing.assert_frame_equal(df, before)


def test_clean_all_reads_every_file(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    dup = ("DUP", "2026-04-30 23:50:00", "2026-05-01 00:10:00")
    make_trips([dup, ("A1", "2026-04-10 10:00:00", "2026-04-10 10:20:00")]).to_csv(
        raw / "202604-tripdata.csv", index=False
    )
    make_trips([dup]).to_csv(raw / "202605-tripdata.csv", index=False)
    dup_file = tmp_path / "dups.csv"
    pd.DataFrame({"ride_id": ["DUP"]}).to_csv(dup_file, index=False)

    out = clean_all(raw, dup_file)

    assert len(out) == 2
    assert out["ride_id"].is_unique


def test_clean_all_raises_when_folder_is_empty(tmp_path):
    with pytest.raises(FileNotFoundError):
        clean_all(tmp_path, tmp_path / "dups.csv")


def good_clean_table():
    df = make_trips(
        [
            ("R1", "2026-01-01 10:00:00", "2026-01-01 10:10:00"),
            ("R2", "2026-01-02 11:00:00", "2026-01-02 11:30:00"),
        ]
    )
    return clean_month(df, "202601-tripdata.csv", set())


def test_validation_passes_on_good_data():
    result = validate_chunks([good_clean_table()], expected_rows=2)
    assert all(result["checks"].values())
    assert result["rows"] == 2


def test_validation_fails_on_wrong_row_count():
    result = validate_chunks([good_clean_table()], expected_rows=3)
    assert result["checks"]["row_count"] is False


def test_validation_finds_duplicate_across_chunks():
    chunk = good_clean_table()
    result = validate_chunks([chunk, chunk])
    assert result["checks"]["no_duplicate_ride_ids"] is False


def test_validation_finds_duplicate_inside_one_chunk():
    chunk = good_clean_table()
    result = validate_chunks([pd.concat([chunk, chunk], ignore_index=True)])
    assert result["checks"]["no_duplicate_ride_ids"] is False


def test_validation_rejects_invalid_categories():
    chunk = good_clean_table()
    chunk.loc[0, "member_casual"] = "subscriber"
    chunk.loc[1, "rideable_type"] = "scooter"
    result = validate_chunks([chunk])
    assert result["checks"]["valid_membership_values"] is False
    assert result["checks"]["valid_bike_types"] is False


def test_missing_values_are_reported_not_failed():
    chunk = good_clean_table()
    chunk.loc[0, "end_lat"] = None
    result = validate_chunks([chunk])
    assert result["missing"]["end_lat"] == 1
    assert all(result["checks"].values())


def test_validate_file_reads_csv_in_chunks(tmp_path):
    path = tmp_path / "clean.csv"
    good_clean_table().to_csv(path, index=False)
    result = validate_file(path, expected_rows=2)
    assert all(result["checks"].values())


@pytest.mark.skipif(
    os.environ.get("CYCLISTIC_FULL_TESTS") != "1" or not config.CLEAN_FILE.exists(),
    reason="full-data test: set CYCLISTIC_FULL_TESTS=1 and build the clean file",
)
def test_real_clean_file_passes_all_checks():
    result = validate_file(config.CLEAN_FILE, config.EXPECTED_CLEAN_ROWS)
    assert all(result["checks"].values())
    assert result["dst_flagged"] == 29
