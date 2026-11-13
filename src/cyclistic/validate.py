"""Check the clean Cyclistic table against the cleaning rules.

The clean file is about 1.6 GB, so it is read in chunks. Checks:
- row count equals the expected 6,115,947;
- no duplicate ride ids;
- member_casual only holds casual or member;
- rideable_type only holds classic_bike or electric_bike;
- no negative ride_length_minutes remain.
It also reports the date range, the DST-flagged rows and missing values per
column. Missing values are reported, not failed: missing stations and end
coordinates are expected and kept (see the cleaning plan).

Run with: python -m cyclistic.validate
"""

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from cyclistic import config


def validate_chunks(
    chunks: Iterable[pd.DataFrame], expected_rows: int | None = None
) -> dict:
    """Run all checks over an iterable of DataFrame chunks.

    Returns a dict with the counts and a "checks" dict of name -> bool.
    """
    total_rows = 0
    missing: dict[str, int] = {}
    bad_membership: set = set()
    bad_bike_types: set = set()
    negative_durations = 0
    dst_flagged = 0
    duplicate_ids: set[str] = set()
    seen_ids: set[str] = set()
    min_start = max_start = None

    for chunk in chunks:
        total_rows += len(chunk)
        for col in chunk.columns:
            missing[col] = missing.get(col, 0) + int(chunk[col].isna().sum())

        bad_membership |= (
            set(chunk["member_casual"].dropna().unique())
            - config.MEMBERSHIP_VALUES
        )
        bad_bike_types |= (
            set(chunk["rideable_type"].dropna().unique())
            - config.BIKE_TYPE_VALUES
        )
        negative_durations += int((chunk["ride_length_minutes"] < 0).sum())
        dst_flagged += int((chunk["duration_dst_flag"] == 1).sum())

        starts = pd.to_datetime(chunk["started_at"])
        chunk_min, chunk_max = starts.min(), starts.max()
        if min_start is None or chunk_min < min_start:
            min_start = chunk_min
        if max_start is None or chunk_max > max_start:
            max_start = chunk_max

        ids = set(chunk["ride_id"].astype(str))
        # A repeat inside one chunk shrinks the set, so compare sizes too.
        if len(ids) < len(chunk):
            duplicate_ids.add("<repeat inside chunk>")
        duplicate_ids |= ids & seen_ids
        seen_ids |= ids

    checks = {
        "no_duplicate_ride_ids": not duplicate_ids,
        "valid_membership_values": not bad_membership,
        "valid_bike_types": not bad_bike_types,
        "no_negative_durations": negative_durations == 0,
    }
    if expected_rows is not None:
        checks["row_count"] = total_rows == expected_rows

    return {
        "rows": total_rows,
        "duplicate_ids": len(duplicate_ids),
        "invalid_membership": bad_membership,
        "invalid_bike_types": bad_bike_types,
        "negative_durations": negative_durations,
        "dst_flagged": dst_flagged,
        "earliest_start": min_start,
        "latest_start": max_start,
        "missing": missing,
        "checks": checks,
    }


def validate_file(path: Path, expected_rows: int | None = None) -> dict:
    """Validate a clean CSV file in chunks."""
    chunks = pd.read_csv(
        path,
        parse_dates=["started_at", "ended_at"],
        chunksize=config.CHUNK_SIZE,
    )
    return validate_chunks(chunks, expected_rows)


def print_report(result: dict) -> None:
    print("=" * 70)
    print("CLEAN DATA VALIDATION")
    print("=" * 70)
    print(f"Rows: {result['rows']:,}")
    for name, passed in result["checks"].items():
        print(f"{name:<28} {'PASS' if passed else 'FAIL'}")
    print(f"DST-flagged records: {result['dst_flagged']:,}")
    print(f"Earliest started_at: {result['earliest_start']}")
    print(f"Latest started_at:   {result['latest_start']}")
    print("\nMissing values per column")
    for col, count in result["missing"].items():
        print(f"{col:<30} {count:>10,}")


def main() -> None:
    result = validate_file(config.CLEAN_FILE, config.EXPECTED_CLEAN_ROWS)
    print_report(result)
    if not all(result["checks"].values()):
        raise SystemExit("Validation FAILED")


if __name__ == "__main__":
    main()
