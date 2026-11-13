"""Clean the 12 monthly Divvy trip files into one analysis-ready table.

Rules (documented in docs/project_management/07_Process_Cleaning_Plan.md):
- remove the confirmed cross-file duplicate rides: a ride id that appears
  in two monthly files is kept only in the file whose month matches the
  month the ride ended;
- keep the original duration in ride_length_minutes_raw;
- flag rides with a negative duration on the daylight-saving date and add
  one hour back to build ride_length_minutes (the analysis duration);
- add day_of_week and month, taken from started_at;
- add source_file so every row can be traced to its raw file.

Run with: python -m cyclistic.clean
"""

from pathlib import Path

import pandas as pd
from tqdm import tqdm

from cyclistic import config


def load_duplicate_ids(duplicate_file: Path) -> set[str]:
    """Return the ride ids confirmed as cross-file duplicates."""
    investigation = pd.read_csv(duplicate_file)
    return set(investigation["ride_id"].astype(str).unique())


def clean_month(
    df: pd.DataFrame, source_file: str, duplicate_ids: set[str]
) -> pd.DataFrame:
    """Clean one monthly file and return a new DataFrame.

    source_file is the raw file name; its first six characters (for example
    202604) are the month the file belongs to.
    """
    df = df.copy()
    df["source_file"] = source_file

    df["started_at"] = pd.to_datetime(df["started_at"], errors="raise")
    df["ended_at"] = pd.to_datetime(df["ended_at"], errors="raise")

    file_month = source_file[:6]
    end_month = df["ended_at"].dt.strftime("%Y%m")
    duplicate_mask = df["ride_id"].astype(str).isin(duplicate_ids) & (
        end_month != file_month
    )
    df = df.loc[~duplicate_mask].copy()

    df["ride_length_minutes_raw"] = (
        df["ended_at"] - df["started_at"]
    ).dt.total_seconds() / 60

    dst_mask = (df["ride_length_minutes_raw"] < 0) & (
        df["started_at"].dt.date == config.DST_FALLBACK_DATE
    )
    df["duration_dst_flag"] = dst_mask.astype(int)

    df["ride_length_minutes"] = df["ride_length_minutes_raw"]
    df.loc[dst_mask, "ride_length_minutes"] += config.DST_CORRECTION_MINUTES

    df["day_of_week"] = df["started_at"].dt.day_name()
    df["month"] = df["started_at"].dt.to_period("M").astype(str)
    return df


def clean_all(raw_dir: Path, duplicate_file: Path) -> pd.DataFrame:
    """Clean every monthly CSV in raw_dir and return one combined table."""
    files = sorted(raw_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    duplicate_ids = load_duplicate_ids(duplicate_file)
    print(f"Confirmed duplicate ride IDs: {len(duplicate_ids):,}")

    parts = []
    for file in tqdm(files, desc="Cleaning files", unit="file"):
        tqdm.write(f"Processing: {file.name}")
        raw = pd.read_csv(file)
        parts.append(clean_month(raw, file.name, duplicate_ids))
    return pd.concat(parts, ignore_index=True)


def main() -> None:
    cleaned = clean_all(config.RAW_DIR, config.DUPLICATE_FILE)
    print(f"Rows after cleaning: {len(cleaned):,}")
    config.CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(config.CLEAN_FILE, index=False)
    print(f"Output: {config.CLEAN_FILE}")


if __name__ == "__main__":
    main()
