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

total_rows = 0
invalid_dates = 0
negative_duration = 0
zero_duration = 0

duration_values = []


# ---------------------------------------------------------
# Process files
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

for file_path in csv_files:

    print(f"Processing: {file_path.name}")

    for chunk in pd.read_csv(
        file_path,
        usecols=[
            "started_at",
            "ended_at"
        ],
        chunksize=100_000
    ):

        total_rows += len(chunk)

        chunk["started_at"] = pd.to_datetime(
            chunk["started_at"],
            errors="coerce"
        )

        chunk["ended_at"] = pd.to_datetime(
            chunk["ended_at"],
            errors="coerce"
        )

        invalid_mask = (
            chunk["started_at"].isna()
            | chunk["ended_at"].isna()
        )

        invalid_dates += invalid_mask.sum()

        valid = chunk[~invalid_mask].copy()

        # Ride duration in minutes
        valid["ride_length_minutes"] = (
            valid["ended_at"] - valid["started_at"]
        ).dt.total_seconds() / 60

        negative_duration += (
            valid["ride_length_minutes"] < 0
        ).sum()

        zero_duration += (
            valid["ride_length_minutes"] == 0
        ).sum()

        duration_values.extend(
            valid["ride_length_minutes"].tolist()
        )


# ---------------------------------------------------------
# Convert durations to Series
# ---------------------------------------------------------

duration_series = pd.Series(
    duration_values,
    name="ride_length_minutes"
)


# ---------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("RIDE DURATION INTEGRITY CHECK")
print("=" * 100)

print(f"Total rows examined:       {total_rows:,}")
print(f"Invalid timestamp rows:    {invalid_dates:,}")
print(f"Negative durations:        {negative_duration:,}")
print(f"Zero-minute durations:     {zero_duration:,}")


print("\n" + "=" * 100)
print("RIDE DURATION DISTRIBUTION")
print("=" * 100)

print(
    duration_series.describe(
        percentiles=[
            0.01,
            0.05,
            0.25,
            0.50,
            0.75,
            0.95,
            0.99,
            0.999
        ]
    ).to_string()
)


# ---------------------------------------------------------
# Additional duration thresholds
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("EXTREME DURATION COUNTS")
print("=" * 100)

thresholds = [
    60,      # 1 hour
    120,     # 2 hours
    180,     # 3 hours
    360,     # 6 hours
    720,     # 12 hours
    1440,    # 24 hours
    2880     # 48 hours
]

for threshold in thresholds:

    count = (
        duration_series > threshold
    ).sum()

    percentage = (
        count / len(duration_series) * 100
    )

    print(
        f"> {threshold:4} minutes "
        f"({threshold / 60:6.1f} hours): "
        f"{count:>10,} "
        f"({percentage:.5f}%)"
    )


# ---------------------------------------------------------
# Longest rides
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("LONGEST 20 RIDE DURATIONS")
print("=" * 100)

print(
    duration_series
    .nlargest(20)
    .to_string(index=False)
)


print("\n" + "=" * 100)
print("CHECK COMPLETE")
print("=" * 100)