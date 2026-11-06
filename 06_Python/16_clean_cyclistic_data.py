import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(
    r"C:\Users\Ali Akbar\Desktop\Portfolio Projects\01_Cyclistic_Bike_Share\02_Raw_Data\extracted"
)

OUTPUT_DIR = Path(
    r"C:\Users\Ali Akbar\Desktop\Portfolio Projects\01_Cyclistic_Bike_Share\03_Clean_Data"
)

DUPLICATE_FILE = Path(
    r"C:\Users\Ali Akbar\Desktop\Portfolio Projects\01_Cyclistic_Bike_Share\01_Project_Management\cross_file_duplicate_investigation.csv"
)

OUTPUT_FILE = OUTPUT_DIR / "cyclistic_clean.csv"

FILES = sorted(DATA_DIR.glob("*.csv"))

# ============================================================
# LOAD CONFIRMED DUPLICATE IDS
# ============================================================

duplicate_investigation = pd.read_csv(DUPLICATE_FILE)

duplicate_ids = set(
    duplicate_investigation["ride_id"].astype(str).unique()
)

print(f"Confirmed duplicate ride IDs: {len(duplicate_ids):,}")

# ============================================================
# PROCESS EACH MONTH
# ============================================================

cleaned_parts = []

for file in FILES:

    print(f"Processing: {file.name}")

    # Read data
    df = pd.read_csv(file)

    # Keep original source file for traceability
    df["source_file"] = file.name

    # Parse timestamps explicitly
    df["started_at"] = pd.to_datetime(
        df["started_at"],
        errors="raise"
    )

    df["ended_at"] = pd.to_datetime(
        df["ended_at"],
        errors="raise"
    )

    # --------------------------------------------------------
    # REMOVE CONFIRMED CROSS-FILE DUPLICATES
    # --------------------------------------------------------

    # File month, e.g. 202604
    file_month = file.name[:6]

    # End month, e.g. 202605
    end_month = df["ended_at"].dt.strftime("%Y%m")

    duplicate_mask = (
        df["ride_id"].astype(str).isin(duplicate_ids)
        & (file_month != end_month)
    )

    removed_duplicates = duplicate_mask.sum()

    if removed_duplicates > 0:
        print(
            f"  Removing duplicate records: "
            f"{removed_duplicates:,}"
        )

    df = df.loc[~duplicate_mask].copy()

    # --------------------------------------------------------
    # RAW RIDE DURATION
    # --------------------------------------------------------

    df["ride_length_minutes_raw"] = (
        (df["ended_at"] - df["started_at"])
        .dt.total_seconds()
        / 60
    )

    # --------------------------------------------------------
    # DST FLAG
    # --------------------------------------------------------

    df["duration_dst_flag"] = 0

    dst_mask = (
        (df["ride_length_minutes_raw"] < 0)
        & (df["started_at"].dt.date == pd.Timestamp("2025-11-02").date())
    )

    df.loc[dst_mask, "duration_dst_flag"] = 1

    # --------------------------------------------------------
    # ANALYTICAL RIDE DURATION
    # --------------------------------------------------------

    df["ride_length_minutes"] = df["ride_length_minutes_raw"]

    # Account for the one-hour DST rollback
    df.loc[dst_mask, "ride_length_minutes"] += 60

    # --------------------------------------------------------
    # DERIVED TIME VARIABLES
    # --------------------------------------------------------

    df["day_of_week"] = df["started_at"].dt.day_name()

    df["month"] = df["started_at"].dt.to_period("M").astype(str)

    # --------------------------------------------------------
    # STORE PROCESSED MONTH
    # --------------------------------------------------------

    cleaned_parts.append(df)


# ============================================================
# COMBINE ALL MONTHS
# ============================================================

cleaned_df = pd.concat(
    cleaned_parts,
    ignore_index=True
)

# ============================================================
# FINAL CHECKS
# ============================================================

print("\n" + "=" * 80)
print("FINAL CLEANING CHECKS")
print("=" * 80)

print(f"Rows after cleaning: {len(cleaned_df):,}")
print(
    f"Unique ride IDs: "
    f"{cleaned_df['ride_id'].nunique():,}"
)

print(
    f"Duplicate ride IDs remaining: "
    f"{cleaned_df['ride_id'].duplicated().sum():,}"
)

print(
    f"DST-flagged records: "
    f"{cleaned_df['duration_dst_flag'].sum():,}"
)

print(
    f"Negative analytical durations remaining: "
    f"{(cleaned_df['ride_length_minutes'] < 0).sum():,}"
)

print(
    f"Missing membership values: "
    f"{cleaned_df['member_casual'].isna().sum():,}"
)

print(
    f"Missing bike-type values: "
    f"{cleaned_df['rideable_type'].isna().sum():,}"
)

# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

cleaned_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 80)
print("CLEANING COMPLETE")
print("=" * 80)

print(f"Output: {OUTPUT_FILE}")