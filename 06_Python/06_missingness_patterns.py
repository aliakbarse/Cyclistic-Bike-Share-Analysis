from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"


# ---------------------------------------------------------
# Counters
# ---------------------------------------------------------

station_pattern_counts = {
    "no_station_missing": 0,
    "start_station_missing_only": 0,
    "end_station_missing_only": 0,
    "both_stations_missing": 0
}

member_counts = {}
bike_type_counts = {}

coordinate_missing_counts = {
    "end_coordinates_missing": 0,
    "start_coordinates_missing": 0
}

total_rows = 0


# ---------------------------------------------------------
# Process files
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in {DATA_FOLDER}"
    )


for file_path in csv_files:

    print(f"Processing: {file_path.name}")

    for chunk in pd.read_csv(
        file_path,
        usecols=[
            "start_station_name",
            "start_station_id",
            "end_station_name",
            "end_station_id",
            "start_lat",
            "start_lng",
            "end_lat",
            "end_lng",
            "member_casual",
            "rideable_type"
        ],
        chunksize=100_000
    ):

        total_rows += len(chunk)

        # -------------------------------------------------
        # Station missingness
        # -------------------------------------------------

        start_station_missing = (
            chunk["start_station_name"].isna()
            | chunk["start_station_id"].isna()
        )

        end_station_missing = (
            chunk["end_station_name"].isna()
            | chunk["end_station_id"].isna()
        )

        no_missing = (
            ~start_station_missing
            & ~end_station_missing
        )

        start_only = (
            start_station_missing
            & ~end_station_missing
        )

        end_only = (
            ~start_station_missing
            & end_station_missing
        )

        both_missing = (
            start_station_missing
            & end_station_missing
        )

        station_pattern_counts["no_station_missing"] += no_missing.sum()
        station_pattern_counts["start_station_missing_only"] += start_only.sum()
        station_pattern_counts["end_station_missing_only"] += end_only.sum()
        station_pattern_counts["both_stations_missing"] += both_missing.sum()

        # -------------------------------------------------
        # Membership pattern
        # -------------------------------------------------

        for member_type, group in chunk.groupby(
            "member_casual",
            dropna=False
        ):

            if member_type not in member_counts:
                member_counts[member_type] = {
                    "total": 0,
                    "station_missing": 0
                }

            member_counts[member_type]["total"] += len(group)

            group_start_missing = (
                group["start_station_name"].isna()
                | group["start_station_id"].isna()
            )

            group_end_missing = (
                group["end_station_name"].isna()
                | group["end_station_id"].isna()
            )

            member_counts[member_type]["station_missing"] += (
                (group_start_missing | group_end_missing).sum()
            )

        # -------------------------------------------------
        # Bike type pattern
        # -------------------------------------------------

        for bike_type, group in chunk.groupby(
            "rideable_type",
            dropna=False
        ):

            if bike_type not in bike_type_counts:
                bike_type_counts[bike_type] = {
                    "total": 0,
                    "station_missing": 0
                }

            bike_type_counts[bike_type]["total"] += len(group)

            group_start_missing = (
                group["start_station_name"].isna()
                | group["start_station_id"].isna()
            )

            group_end_missing = (
                group["end_station_name"].isna()
                | group["end_station_id"].isna()
            )

            bike_type_counts[bike_type]["station_missing"] += (
                (group_start_missing | group_end_missing).sum()
            )

        # -------------------------------------------------
        # Coordinate missingness
        # -------------------------------------------------

        coordinate_missing_counts[
            "end_coordinates_missing"
        ] += (
            chunk["end_lat"].isna()
            | chunk["end_lng"].isna()
        ).sum()

        coordinate_missing_counts[
            "start_coordinates_missing"
        ] += (
            chunk["start_lat"].isna()
            | chunk["start_lng"].isna()
        ).sum()


# =========================================================
# RESULTS
# =========================================================

print("\n" + "=" * 100)
print("STATION MISSINGNESS PATTERNS")
print("=" * 100)

for pattern, count in station_pattern_counts.items():

    percentage = (
        count / total_rows * 100
    )

    print(
        f"{pattern:<30} "
        f"{count:>12,} "
        f"({percentage:.4f}%)"
    )


# ---------------------------------------------------------
# Membership results
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("STATION MISSINGNESS BY MEMBERSHIP TYPE")
print("=" * 100)

for member_type, values in member_counts.items():

    percentage = (
        values["station_missing"]
        / values["total"]
        * 100
    )

    print(
        f"{member_type:<15} "
        f"Total: {values['total']:>12,} "
        f"Station missing: {values['station_missing']:>12,} "
        f"({percentage:.2f}%)"
    )


# ---------------------------------------------------------
# Bike type results
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("STATION MISSINGNESS BY BIKE TYPE")
print("=" * 100)

for bike_type, values in bike_type_counts.items():

    percentage = (
        values["station_missing"]
        / values["total"]
        * 100
    )

    print(
        f"{bike_type:<25} "
        f"Total: {values['total']:>12,} "
        f"Station missing: {values['station_missing']:>12,} "
        f"({percentage:.2f}%)"
    )


# ---------------------------------------------------------
# Coordinate results
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("COORDINATE MISSINGNESS")
print("=" * 100)

for field, count in coordinate_missing_counts.items():

    percentage = count / total_rows * 100

    print(
        f"{field:<30} "
        f"{count:>12,} "
        f"({percentage:.4f}%)"
    )


print("\n" + "=" * 100)
print(f"Total rows examined: {total_rows:,}")
print("=" * 100)