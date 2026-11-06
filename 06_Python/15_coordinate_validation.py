import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(
    r"C:\Users\Ali Akbar\Desktop\Portfolio Projects\01_Cyclistic_Bike_Share\02_Raw_Data\extracted"
)

FILES = sorted(DATA_DIR.glob("*.csv"))

# ============================================================
# INITIAL COUNTERS
# ============================================================

total_rows = 0

coordinate_columns = [
    "start_lat",
    "start_lng",
    "end_lat",
    "end_lng"
]

missing_counts = {col: 0 for col in coordinate_columns}
zero_counts = {col: 0 for col in coordinate_columns}
invalid_counts = {col: 0 for col in coordinate_columns}

# Rows with suspicious Chicago-area coordinates
suspicious_geography_count = 0

# Broad geographic screening box.
# This is NOT a cleaning rule; it is only an anomaly check.
LAT_MIN = 40.0
LAT_MAX = 43.0
LNG_MIN = -90.0
LNG_MAX = -86.0

# ============================================================
# PROCESS FILES
# ============================================================

for file in FILES:

    print(f"Processing: {file.name}")

    for chunk in pd.read_csv(
        file,
        usecols=coordinate_columns,
        chunksize=100_000
    ):

        total_rows += len(chunk)

        # ----------------------------------------------------
        # Missing values
        # ----------------------------------------------------

        for col in coordinate_columns:
            missing_counts[col] += chunk[col].isna().sum()

        # ----------------------------------------------------
        # Zero values
        # ----------------------------------------------------

        for col in coordinate_columns:
            zero_counts[col] += (chunk[col] == 0).sum()

        # ----------------------------------------------------
        # Technical validity
        # ----------------------------------------------------

        invalid_counts["start_lat"] += (
            (~chunk["start_lat"].between(-90, 90, inclusive="both"))
            & chunk["start_lat"].notna()
        ).sum()

        invalid_counts["start_lng"] += (
            (~chunk["start_lng"].between(-180, 180, inclusive="both"))
            & chunk["start_lng"].notna()
        ).sum()

        invalid_counts["end_lat"] += (
            (~chunk["end_lat"].between(-90, 90, inclusive="both"))
            & chunk["end_lat"].notna()
        ).sum()

        invalid_counts["end_lng"] += (
            (~chunk["end_lng"].between(-180, 180, inclusive="both"))
            & chunk["end_lng"].notna()
        ).sum()

        # ----------------------------------------------------
        # Geographic plausibility screening
        # ----------------------------------------------------

        start_geo_suspicious = (
            (
                (chunk["start_lat"] < LAT_MIN)
                | (chunk["start_lat"] > LAT_MAX)
                | (chunk["start_lng"] < LNG_MIN)
                | (chunk["start_lng"] > LNG_MAX)
            )
            & chunk["start_lat"].notna()
            & chunk["start_lng"].notna()
        )

        end_geo_suspicious = (
            (
                (chunk["end_lat"] < LAT_MIN)
                | (chunk["end_lat"] > LAT_MAX)
                | (chunk["end_lng"] < LNG_MIN)
                | (chunk["end_lng"] > LNG_MAX)
            )
            & chunk["end_lat"].notna()
            & chunk["end_lng"].notna()
        )

        suspicious_geography_count += (
            start_geo_suspicious | end_geo_suspicious
        ).sum()

# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 100)
print("COORDINATE VALIDATION")
print("=" * 100)

print(f"\nTotal rows checked: {total_rows:,}")

print("\n" + "=" * 100)
print("MISSING COORDINATES")
print("=" * 100)

for col in coordinate_columns:
    count = missing_counts[col]
    percentage = count / total_rows * 100
    print(f"{col:<12} {count:>10,}  ({percentage:.4f}%)")

print("\n" + "=" * 100)
print("ZERO COORDINATES")
print("=" * 100)

for col in coordinate_columns:
    count = zero_counts[col]
    print(f"{col:<12} {count:>10,}")

print("\n" + "=" * 100)
print("TECHNICALLY INVALID COORDINATES")
print("=" * 100)

for col in coordinate_columns:
    count = invalid_counts[col]
    print(f"{col:<12} {count:>10,}")

print("\n" + "=" * 100)
print("GEOGRAPHIC PLAUSIBILITY SCREEN")
print("=" * 100)

print(
    f"Rows with at least one coordinate outside the broad "
    f"Chicago-area screening box: {suspicious_geography_count:,}"
)

print(
    "\nScreening box used:"
    f"\nLatitude:  {LAT_MIN} to {LAT_MAX}"
    f"\nLongitude: {LNG_MIN} to {LNG_MAX}"
)

print(
    "\nNOTE: Geographic screening flags potentially unusual records; "
    "it does not prove that those records are erroneous."
)