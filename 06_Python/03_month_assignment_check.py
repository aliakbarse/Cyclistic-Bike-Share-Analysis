from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"

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

    if expected_month == 12:
        expected_end = pd.Timestamp(
            year=expected_year + 1,
            month=1,
            day=1
        )
    else:
        expected_end = pd.Timestamp(
            year=expected_year,
            month=expected_month + 1,
            day=1
        )

    df = pd.read_csv(
        file_path,
        usecols=["started_at", "ended_at"]
    )

    df["started_at"] = pd.to_datetime(
        df["started_at"],
        errors="coerce"
    )

    df["ended_at"] = pd.to_datetime(
        df["ended_at"],
        errors="coerce"
    )

    valid_started = df["started_at"].notna()
    valid_ended = df["ended_at"].notna()

    # Check whether ended_at belongs to the expected month
    ended_in_expected_month = (
        (df["ended_at"] >= expected_start)
        & (df["ended_at"] < expected_end)
    )

    ended_outside_expected_month = (
        valid_ended & ~ended_in_expected_month
    )

    print("\n" + "=" * 90)
    print(file_path.name)
    print("=" * 90)

    print(f"Total rows:                    {len(df):,}")
    print(f"Valid ended_at:                {valid_ended.sum():,}")
    print(
        f"Ended in expected month:      "
        f"{ended_in_expected_month.sum():,}"
    )
    print(
        f"Ended outside expected month:"
        f" {ended_outside_expected_month.sum():,}"
    )

    if ended_outside_expected_month.any():

        print("\nExamples outside expected month:")

        print(
            df.loc[
                ended_outside_expected_month,
                ["started_at", "ended_at"]
            ]
            .sort_values("ended_at")
            .head(10)
            .to_string(index=False)
        )