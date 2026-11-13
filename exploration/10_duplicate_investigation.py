from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"

TARGET_FILE = DATA_FOLDER / "202605-divvy-tripdata.csv"


# ---------------------------------------------------------
# First pass:
# Find duplicate ride IDs across the ENTIRE file
# ---------------------------------------------------------

seen_ids = set()
duplicate_ids = set()
duplicate_occurrences = 0

for chunk in pd.read_csv(
    TARGET_FILE,
    usecols=["ride_id"],
    dtype={"ride_id": "string"},
    chunksize=100_000
):

    for ride_id in chunk["ride_id"].dropna():

        if ride_id in seen_ids:
            duplicate_ids.add(ride_id)
            duplicate_occurrences += 1
        else:
            seen_ids.add(ride_id)


print("=" * 100)
print("DUPLICATE RIDE ID INVESTIGATION")
print("=" * 100)

print(f"Total unique ride IDs seen:      {len(seen_ids):,}")
print(f"Distinct duplicated ride IDs:   {len(duplicate_ids):,}")
print(f"Duplicate row occurrences:      {duplicate_occurrences:,}")


# ---------------------------------------------------------
# Second pass:
# Retrieve complete duplicate records
# ---------------------------------------------------------

duplicate_rows = []

for chunk in pd.read_csv(
    TARGET_FILE,
    dtype={"ride_id": "string"},
    chunksize=100_000
):

    matches = chunk[
        chunk["ride_id"].isin(duplicate_ids)
    ]

    if not matches.empty:
        duplicate_rows.append(matches)


if duplicate_rows:

    duplicates_df = pd.concat(
        duplicate_rows,
        ignore_index=True
    )

else:

    duplicates_df = pd.DataFrame()


# ---------------------------------------------------------
# Analyze duplicates
# ---------------------------------------------------------

if not duplicates_df.empty:

    duplicates_df = duplicates_df.sort_values(
        ["ride_id", "started_at"]
    )

    print("\n" + "=" * 100)
    print("DUPLICATE COUNTS BY RIDE ID")
    print("=" * 100)

    counts = (
        duplicates_df
        .groupby("ride_id")
        .size()
        .sort_values(ascending=False)
    )

    print(counts.to_string())


    # -----------------------------------------------------
    # Exact vs conflicting duplicate records
    # -----------------------------------------------------

    exact_duplicate_ids = 0
    conflicting_duplicate_ids = 0

    for ride_id, group in duplicates_df.groupby("ride_id"):

        unique_rows = len(
            group.drop_duplicates()
        )

        if unique_rows == 1:
            exact_duplicate_ids += 1
        else:
            conflicting_duplicate_ids += 1


    print("\n" + "=" * 100)
    print("EXACT DUPLICATE CHECK")
    print("=" * 100)

    print(
        f"Ride IDs with identical duplicate rows: "
        f"{exact_duplicate_ids:,}"
    )

    print(
        f"Ride IDs with conflicting duplicate rows: "
        f"{conflicting_duplicate_ids:,}"
    )


    # -----------------------------------------------------
    # Display complete records
    # -----------------------------------------------------

    print("\n" + "=" * 100)
    print("COMPLETE DUPLICATE RECORDS")
    print("=" * 100)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 250)

    print(
        duplicates_df.to_string(index=False)
    )


    # -----------------------------------------------------
    # Save results
    # -----------------------------------------------------

    output_file = (
        PROJECT_ROOT
        / "01_Project_Management"
        / "duplicate_investigation.csv"
    )

    duplicates_df.to_csv(
        output_file,
        index=False
    )

    print("\nInvestigation saved to:")
    print(output_file.resolve())

else:

    print("\nNo duplicate records were found.")


print("\n" + "=" * 100)
print("INVESTIGATION COMPLETE")
print("=" * 100)