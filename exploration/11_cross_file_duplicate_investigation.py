from pathlib import Path
import pandas as pd
from collections import defaultdict


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"


# ---------------------------------------------------------
# Pass 1:
# Count every ride_id across ALL 12 files
# ---------------------------------------------------------

ride_id_files = defaultdict(set)
total_rows = 0

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

for file_path in csv_files:

    print(f"Scanning IDs: {file_path.name}")

    for chunk in pd.read_csv(
        file_path,
        usecols=["ride_id"],
        dtype={"ride_id": "string"},
        chunksize=100_000
    ):

        total_rows += len(chunk)

        valid_ids = chunk["ride_id"].dropna()

        for ride_id in valid_ids:
            ride_id_files[ride_id].add(file_path.name)


# ---------------------------------------------------------
# Identify IDs appearing in multiple files
# ---------------------------------------------------------

cross_file_ids = {
    ride_id: files
    for ride_id, files in ride_id_files.items()
    if len(files) > 1
}


print("\n" + "=" * 100)
print("CROSS-FILE DUPLICATE CHECK")
print("=" * 100)

print(f"Total rows:                    {total_rows:,}")
print(f"Unique ride IDs:               {len(ride_id_files):,}")
print(f"Ride IDs in multiple files:    {len(cross_file_ids):,}")

for ride_id, files in list(cross_file_ids.items())[:50]:
    print(
        f"{ride_id} -> "
        f"{', '.join(sorted(files))}"
    )


# ---------------------------------------------------------
# Pass 2:
# Retrieve complete rows for cross-file duplicate IDs
# ---------------------------------------------------------

duplicate_rows = []

if cross_file_ids:

    duplicate_id_set = set(cross_file_ids.keys())

    for file_path in csv_files:

        print(f"Retrieving duplicates: {file_path.name}")

        for chunk in pd.read_csv(
            file_path,
            dtype={"ride_id": "string"},
            chunksize=100_000
        ):

            matches = chunk[
                chunk["ride_id"].isin(duplicate_id_set)
            ]

            if not matches.empty:

                matches = matches.copy()
                matches["source_file"] = file_path.name

                duplicate_rows.append(matches)


# ---------------------------------------------------------
# Analyze complete duplicate records
# ---------------------------------------------------------

if duplicate_rows:

    duplicates_df = pd.concat(
        duplicate_rows,
        ignore_index=True
    )

    duplicates_df = duplicates_df.sort_values(
        ["ride_id", "source_file"]
    )


    print("\n" + "=" * 100)
    print("COMPLETE CROSS-FILE DUPLICATE RECORDS")
    print("=" * 100)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 250)

    print(
        duplicates_df.to_string(index=False)
    )


    # -----------------------------------------------------
    # Exact vs conflicting records
    # -----------------------------------------------------

    exact_duplicate_ids = 0
    conflicting_duplicate_ids = 0

    comparison_columns = [
        column
        for column in duplicates_df.columns
        if column != "source_file"
    ]

    for ride_id, group in duplicates_df.groupby("ride_id"):

        unique_records = len(
            group[comparison_columns]
            .drop_duplicates()
        )

        if unique_records == 1:
            exact_duplicate_ids += 1
        else:
            conflicting_duplicate_ids += 1


    print("\n" + "=" * 100)
    print("DUPLICATE RECORD TYPE")
    print("=" * 100)

    print(
        f"IDs duplicated across files:       "
        f"{len(cross_file_ids):,}"
    )

    print(
        f"Exact duplicate records:            "
        f"{exact_duplicate_ids:,}"
    )

    print(
        f"Conflicting duplicate records:      "
        f"{conflicting_duplicate_ids:,}"
    )


    # -----------------------------------------------------
    # Save investigation
    # -----------------------------------------------------

    output_file = (
        PROJECT_ROOT
        / "01_Project_Management"
        / "cross_file_duplicate_investigation.csv"
    )

    duplicates_df.to_csv(
        output_file,
        index=False
    )

    print("\nInvestigation saved to:")
    print(output_file.resolve())

else:

    print("\nNo cross-file duplicate ride IDs were found.")


print("\n" + "=" * 100)
print("INVESTIGATION COMPLETE")
print("=" * 100)