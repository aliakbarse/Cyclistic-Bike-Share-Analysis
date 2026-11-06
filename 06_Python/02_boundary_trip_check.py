from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"


# ---------------------------------------------------------
# Inspect monthly boundary records
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

for file_path in csv_files:

    period = file_path.name[:6]

    expected_year = int(period[:4])
    expected_month = int(period[4:6])

    expected_start = pd.Timestamp(
        year=expected_year,
        month=expected_month,
        day=1
    )

    # Determine the start of the next month
    if expected_month == 12:
        next_month_start = pd.Timestamp(
            year=expected_year + 1,
            month=1,
            day=1
        )
    else:
        next_month_start = pd.Timestamp(
            year=expected_year,
            month=expected_month + 1,
            day=1
        )

    # Read only columns needed for this investigation
    df = pd.read_csv(
        file_path,
        usecols=[
            "ride_id",
            "started_at",
            "ended_at",
            "member_casual"
        ]
    )

    df["started_at"] = pd.to_datetime(
        df["started_at"],
        errors="coerce"
    )

    df["ended_at"] = pd.to_datetime(
        df["ended_at"],
        errors="coerce"
    )

    # Select trips that started before the expected month
    boundary = df[df["started_at"] < expected_start].copy()

    print("\n" + "=" * 100)
    print(file_path.name)
    print("=" * 100)

    print(f"Boundary records: {len(boundary):,}")

    if boundary.empty:
        print("No previous-month records.")
        continue

    # Count whether these trips ended in the expected month
    ended_in_expected_month = (
        (boundary["ended_at"] >= expected_start)
        & (boundary["ended_at"] < next_month_start)
    ).sum()

    ended_before_expected_month = (
        boundary["ended_at"] < expected_start
    ).sum()

    ended_after_expected_month = (
        boundary["ended_at"] >= next_month_start
    ).sum()

    print(
        f"Started previous month, ended in expected month: "
        f"{ended_in_expected_month:,}"
    )

    print(
        f"Started previous month, ended before expected month: "
        f"{ended_before_expected_month:,}"
    )

    print(
        f"Started previous month, ended after expected month: "
        f"{ended_after_expected_month:,}"
    )

    print("\nSample boundary records:")

    print(
        boundary[
            [
                "ride_id",
                "started_at",
                "ended_at",
                "member_casual"
            ]
        ]
        .sort_values("started_at")
        .head(10)
        .to_string(index=False)
    )