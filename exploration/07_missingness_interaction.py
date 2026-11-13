from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"


# ---------------------------------------------------------
# Store results
# ---------------------------------------------------------

results = []


# ---------------------------------------------------------
# Process files
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

for file_path in csv_files:

    print(f"Processing: {file_path.name}")

    for chunk in pd.read_csv(
        file_path,
        usecols=[
            "start_station_name",
            "start_station_id",
            "end_station_name",
            "end_station_id",
            "member_casual",
            "rideable_type"
        ],
        chunksize=100_000
    ):

        # -------------------------------------------------
        # Define station missingness
        # -------------------------------------------------

        start_missing = (
            chunk["start_station_name"].isna()
            | chunk["start_station_id"].isna()
        )

        end_missing = (
            chunk["end_station_name"].isna()
            | chunk["end_station_id"].isna()
        )

        station_missing = start_missing | end_missing

        chunk["station_missing"] = station_missing

        # -------------------------------------------------
        # Aggregate by member + bike type
        # -------------------------------------------------

        grouped = (
            chunk
            .groupby(
                ["member_casual", "rideable_type"],
                dropna=False
            )
            .agg(
                total_trips=("station_missing", "size"),
                station_missing_trips=("station_missing", "sum")
            )
            .reset_index()
        )

        results.append(grouped)


# ---------------------------------------------------------
# Combine chunk results
# ---------------------------------------------------------

results_df = pd.concat(
    results,
    ignore_index=True
)


# ---------------------------------------------------------
# Re-aggregate
# ---------------------------------------------------------

results_df = (
    results_df
    .groupby(
        ["member_casual", "rideable_type"],
        as_index=False
    )
    .agg(
        total_trips=("total_trips", "sum"),
        station_missing_trips=("station_missing_trips", "sum")
    )
)


# ---------------------------------------------------------
# Calculate percentage
# ---------------------------------------------------------

results_df["station_missing_pct"] = (
    results_df["station_missing_trips"]
    / results_df["total_trips"]
    * 100
)


# ---------------------------------------------------------
# Display
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("STATION MISSINGNESS BY MEMBERSHIP AND BIKE TYPE")
print("=" * 100)

print(
    results_df.to_string(index=False)
)


# ---------------------------------------------------------
# Pivot for easier interpretation
# ---------------------------------------------------------

pivot = results_df.pivot(
    index="member_casual",
    columns="rideable_type",
    values="station_missing_pct"
)

print("\n" + "=" * 100)
print("MISSINGNESS % MATRIX")
print("=" * 100)

print(pivot.to_string())