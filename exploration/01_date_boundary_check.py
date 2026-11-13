from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"


# ---------------------------------------------------------
# Expected month from filename
# ---------------------------------------------------------

def expected_month(file_name):
    """
    Extract YYYYMM from the beginning of the filename.
    Example: 202509-divvy-tripdata.csv -> 202509
    """
    return file_name[:6]


# ---------------------------------------------------------
# Inspect files
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in {DATA_FOLDER}"
    )


for file_path in csv_files:

    period = expected_month(file_path.name)

    print("\n" + "=" * 90)
    print(f"{file_path.name}")
    print("=" * 90)

    # Read only the started_at column
    df = pd.read_csv(
        file_path,
        usecols=["started_at"]
    )

    df["started_at"] = pd.to_datetime(
        df["started_at"],
        errors="coerce"
    )

    # Remove invalid dates for this check
    valid_dates = df["started_at"].dropna()

    # Expected year and month
    expected_year = int(period[:4])
    expected_month_number = int(period[4:6])

    # Count records in expected month
    expected_count = (
        (valid_dates.dt.year == expected_year)
        & (valid_dates.dt.month == expected_month_number)
    ).sum()

    # Count records before expected month
    before_count = (
        (valid_dates < valid_dates.dt.to_period("M").min().start_time)
    ).sum()

    # Calculate previous-month condition explicitly
    expected_start = pd.Timestamp(
        year=expected_year,
        month=expected_month_number,
        day=1
    )

    previous_month_count = (
        valid_dates < expected_start
    ).sum()

    # Count records after expected month
    if expected_month_number == 12:
        next_month_start = pd.Timestamp(
            year=expected_year + 1,
            month=1,
            day=1
        )
    else:
        next_month_start = pd.Timestamp(
            year=expected_year,
            month=expected_month_number + 1,
            day=1
        )

    after_count = (
        valid_dates >= next_month_start
    ).sum()

    print(f"Rows with valid dates:      {len(valid_dates):,}")
    print(f"Minimum started_at:         {valid_dates.min()}")
    print(f"Maximum started_at:         {valid_dates.max()}")
    print(f"Expected-month records:     {expected_count:,}")
    print(f"Previous-month records:     {previous_month_count:,}")
    print(f"Next-month records:         {after_count:,}")

    # Show earliest 5 dates
    print("\nEarliest 5 started_at values:")
    print(valid_dates.nsmallest(5).to_string(index=False))

    # Show latest 5 dates
    print("\nLatest 5 started_at values:")
    print(valid_dates.nlargest(5).sort_values().to_string(index=False))