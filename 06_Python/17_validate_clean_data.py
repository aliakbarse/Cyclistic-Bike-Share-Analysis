import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

CLEAN_FILE = Path(
    r"C:\Users\Ali Akbar\Desktop\Portfolio Projects\01_Cyclistic_Bike_Share\03_Clean_Data\cyclistic_clean.csv"
)

CHUNK_SIZE = 100_000

EXPECTED_ROWS = 6_115_947

EXPECTED_MEMBERSHIP = {"casual", "member"}
EXPECTED_BIKE_TYPES = {"classic_bike", "electric_bike"}


# ============================================================
# VALIDATION
# ============================================================

total_rows = 0
missing_counts = {}
invalid_categories = set()
invalid_bike_types = set()
negative_duration_count = 0
dst_flag_count = 0

min_start = None
max_start = None

duplicate_ids = set()
seen_ids = set()

first_chunk = True

for chunk in pd.read_csv(
    CLEAN_FILE,
    parse_dates=["started_at", "ended_at"],
    chunksize=CHUNK_SIZE
):

    total_rows += len(chunk)

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    if first_chunk:
        missing_counts = {
            col: 0 for col in chunk.columns
        }
        first_chunk = False

    for col in chunk.columns:
        missing_counts[col] += chunk[col].isna().sum()

    # --------------------------------------------------------
    # Categorical integrity
    # --------------------------------------------------------

    invalid_categories.update(
        set(chunk["member_casual"].dropna().unique())
        - EXPECTED_MEMBERSHIP
    )

    invalid_bike_types.update(
        set(chunk["rideable_type"].dropna().unique())
        - EXPECTED_BIKE_TYPES
    )

    # --------------------------------------------------------
    # Duration
    # --------------------------------------------------------

    negative_duration_count += (
        chunk["ride_length_minutes"] < 0
    ).sum()

    dst_flag_count += (
        chunk["duration_dst_flag"] == 1
    ).sum()

    # --------------------------------------------------------
    # Date range
    # --------------------------------------------------------

    chunk_min = chunk["started_at"].min()
    chunk_max = chunk["started_at"].max()

    if min_start is None or chunk_min < min_start:
        min_start = chunk_min

    if max_start is None or chunk_max > max_start:
        max_start = chunk_max

    # --------------------------------------------------------
    # Duplicate IDs
    # --------------------------------------------------------

    current_ids = set(chunk["ride_id"].astype(str))

    duplicate_ids.update(
        current_ids.intersection(seen_ids)
    )

    seen_ids.update(current_ids)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 80)
print("CLEAN DATA VALIDATION")
print("=" * 80)

print(f"Rows: {total_rows:,}")
print(f"Expected rows: {EXPECTED_ROWS:,}")
print(
    f"Row count check: "
    f"{'PASS' if total_rows == EXPECTED_ROWS else 'FAIL'}"
)

print(f"\nDuplicate ride IDs: {len(duplicate_ids):,}")
print(
    f"Duplicate check: "
    f"{'PASS' if len(duplicate_ids) == 0 else 'FAIL'}"
)

print(f"\nInvalid membership values: {invalid_categories or 'None'}")
print(
    f"Membership check: "
    f"{'PASS' if not invalid_categories else 'FAIL'}"
)

print(f"\nInvalid bike types: {invalid_bike_types or 'None'}")
print(
    f"Bike-type check: "
    f"{'PASS' if not invalid_bike_types else 'FAIL'}"
)

print(f"\nNegative analytical durations: {negative_duration_count:,}")
print(
    f"Duration check: "
    f"{'PASS' if negative_duration_count == 0 else 'FAIL'}"
)

print(f"\nDST-flagged records: {dst_flag_count:,}")

print("\n" + "=" * 80)
print("DATE RANGE")
print("=" * 80)

print(f"Earliest started_at: {min_start}")
print(f"Latest started_at:   {max_start}")

print("\n" + "=" * 80)
print("MISSING VALUES")
print("=" * 80)

for col, count in missing_counts.items():
    print(f"{col:<30} {count:>10,}")

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)