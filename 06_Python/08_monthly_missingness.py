from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

results = []


# ---------------------------------------------------------
# Process each month
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

for file_path in csv_files:

    print(f"Processing: {file_path.name}")

    monthly_results = []

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

        start_missing = (
            chunk["start_station_name"].isna()
            | chunk["start_station_id"].isna()
        )

        end_missing = (
            chunk["end_station_name"].isna()
            | chunk["end_station_id"].isna()
        )

        chunk["station_missing"] = (
            start_missing | end_missing
        )

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

        monthly_results.append(grouped)

    month_df = pd.concat(
        monthly_results,
        ignore_index=True
    )

    month_df = (
        month_df
        .groupby(
            ["member_casual", "rideable_type"],
            as_index=False
        )
        .agg(
            total_trips=("total_trips", "sum"),
            station_missing_trips=("station_missing_trips", "sum")
        )
    )

    month_df["station_missing_pct"] = (
        month_df["station_missing_trips"]
        / month_df["total_trips"]
        * 100
    )

    month_df["file_name"] = file_path.name

    results.append(month_df)


# ---------------------------------------------------------
# Combine all months
# ---------------------------------------------------------

results_df = pd.concat(
    results,
    ignore_index=True
)

results_df = results_df[
    [
        "file_name",
        "member_casual",
        "rideable_type",
        "total_trips",
        "station_missing_trips",
        "station_missing_pct"
    ]
]


# ---------------------------------------------------------
# Display
# ---------------------------------------------------------

print("\n" + "=" * 110)
print("MONTHLY STATION MISSINGNESS BY MEMBERSHIP AND BIKE TYPE")
print("=" * 110)

print(
    results_df.to_string(index=False)
)


# ---------------------------------------------------------
# Electric-bike summary
# ---------------------------------------------------------

electric = results_df[
    results_df["rideable_type"] == "electric_bike"
].copy()

print("\n" + "=" * 110)
print("ELECTRIC-BIKE MISSINGNESS BY MONTH")
print("=" * 110)

print(
    electric[
        [
            "file_name",
            "member_casual",
            "station_missing_pct"
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# Overall monthly summary
# ---------------------------------------------------------

monthly_overall = (
    results_df
    .groupby("file_name")
    .agg(
        total_trips=("total_trips", "sum"),
        station_missing_trips=("station_missing_trips", "sum")
    )
    .reset_index()
)

monthly_overall["station_missing_pct"] = (
    monthly_overall["station_missing_trips"]
    / monthly_overall["total_trips"]
    * 100
)

print("\n" + "=" * 110)
print("OVERALL STATION MISSINGNESS BY MONTH")
print("=" * 110)

print(
    monthly_overall.to_string(index=False)
)