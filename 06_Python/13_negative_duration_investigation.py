from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"


# ---------------------------------------------------------
# Find negative-duration trips
# ---------------------------------------------------------

negative_rows = []

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

for file_path in csv_files:

    print(f"Checking: {file_path.name}")

    for chunk in pd.read_csv(
        file_path,
        usecols=[
            "ride_id",
            "rideable_type",
            "started_at",
            "ended_at",
            "start_station_name",
            "start_station_id",
            "end_station_name",
            "end_station_id",
            "member_casual"
        ],
        dtype={"ride_id": "string"},
        chunksize=100_000
    ):

        chunk["started_at"] = pd.to_datetime(
            chunk["started_at"],
            errors="coerce"
        )

        chunk["ended_at"] = pd.to_datetime(
            chunk["ended_at"],
            errors="coerce"
        )

        chunk["ride_length_minutes"] = (
            chunk["ended_at"] - chunk["started_at"]
        ).dt.total_seconds() / 60

        negative = chunk[
            chunk["ride_length_minutes"] < 0
        ].copy()

        if not negative.empty:
            negative["source_file"] = file_path.name
            negative_rows.append(negative)


# ---------------------------------------------------------
# Combine
# ---------------------------------------------------------

if not negative_rows:
    print("\nNo negative-duration records found.")
    raise SystemExit


negative_df = pd.concat(
    negative_rows,
    ignore_index=True
)

negative_df = negative_df.sort_values(
    "ride_length_minutes"
)


# ---------------------------------------------------------
# Display
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("NEGATIVE-DURATION TRIPS")
print("=" * 100)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)

print(
    negative_df.to_string(index=False)
)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

print(
    f"Negative-duration records: "
    f"{len(negative_df):,}"
)

print(
    f"Most negative duration: "
    f"{negative_df['ride_length_minutes'].min():.2f} minutes"
)

print(
    f"Least negative duration: "
    f"{negative_df['ride_length_minutes'].max():.2f} minutes"
)


# ---------------------------------------------------------
# Distribution by membership
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("BY MEMBERSHIP TYPE")
print("=" * 100)

print(
    negative_df["member_casual"]
    .value_counts(dropna=False)
    .to_string()
)


# ---------------------------------------------------------
# Distribution by bike type
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("BY BIKE TYPE")
print("=" * 100)

print(
    negative_df["rideable_type"]
    .value_counts(dropna=False)
    .to_string()
)


# ---------------------------------------------------------
# Source file distribution
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("BY SOURCE FILE")
print("=" * 100)

print(
    negative_df["source_file"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

output_file = (
    PROJECT_ROOT
    / "01_Project_Management"
    / "negative_duration_investigation.csv"
)

negative_df.to_csv(
    output_file,
    index=False
)

print("\nInvestigation saved to:")
print(output_file.resolve())