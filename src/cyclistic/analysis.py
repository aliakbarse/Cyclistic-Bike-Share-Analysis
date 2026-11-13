"""Analysis functions for the clean Cyclistic table.

These are the definitions behind every finding in docs/findings.md. They
are plain pandas functions, so each one can be tested on a few rows.

Definitions (the same ones the SQL in sql/04_final_queries.sql uses):
- weekend: Saturday or Sunday, from day_of_week;
- season and month: taken from the first six characters of source_file
  (for example 202607), so a ride that crosses midnight at the end of a
  month stays in the month of its file; summer is June, July, August;
- commute-like ride: starts on a weekday, in the 06:00-09:59 or
  16:00-19:59 window, and lasts under 30 minutes. This describes timing and
  length only. The data has no trip purpose.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from cyclistic import config

RIDER_ORDER = ["member", "casual"]
WEEKEND_DAYS = ("Saturday", "Sunday")
SUMMER_MONTHS = ("06", "07", "08")
SEASON = {
    "12": "Winter", "01": "Winter", "02": "Winter",
    "03": "Spring", "04": "Spring", "05": "Spring",
    "06": "Summer", "07": "Summer", "08": "Summer",
    "09": "Autumn", "10": "Autumn", "11": "Autumn",
}
COMMUTE_WINDOWS = ((6, 9), (16, 19))  # start hours, both ends included
COMMUTE_MAX_MINUTES = 30
DURATION_LABELS = ["<15 min", "15-29 min", "30-59 min", "60+ min"]
WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]

USECOLS = [
    "ride_id", "rideable_type", "started_at", "start_station_name",
    "start_station_id", "end_station_id", "member_casual", "source_file",
    "ride_length_minutes", "day_of_week",
]
DTYPES = {
    "rideable_type": "category", "member_casual": "category",
    "source_file": "category", "day_of_week": "category",
    "start_station_id": "category", "end_station_id": "category",
    "start_station_name": "category",
}


def load_clean(path: Path = config.CLEAN_FILE) -> pd.DataFrame:
    """Read the clean file with only the columns the analysis needs.

    Timestamps carry one to three fractional-second digits, so they are
    parsed with format="ISO8601".
    """
    df = pd.read_csv(path, usecols=USECOLS, dtype=DTYPES)
    df["started_at"] = pd.to_datetime(df["started_at"], format="ISO8601")
    return df


def add_analysis_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with the fields used by the analysis."""
    df = df.copy()
    df["hour"] = df["started_at"].dt.hour.astype("int8")
    df["is_weekend"] = df["day_of_week"].astype(str).isin(WEEKEND_DAYS)
    df["analysis_month"] = df["source_file"].astype(str).str[:6]
    df["season"] = df["analysis_month"].str[4:6].map(SEASON)
    df["day_type"] = np.where(df["is_weekend"], "Weekend", "Weekday")
    df["summer"] = df["season"].eq("Summer")
    df["duration_bucket"] = pd.cut(
        df["ride_length_minutes"],
        [-np.inf, 15, 30, 60, np.inf],
        labels=DURATION_LABELS,
        right=False,
    )
    df["electric"] = df["rideable_type"].astype(str).eq("electric_bike")

    in_window = np.zeros(len(df), dtype=bool)
    for first, last in COMMUTE_WINDOWS:
        in_window |= df["hour"].between(first, last).to_numpy()
    df["commute_like"] = (
        ~df["is_weekend"]
        & in_window
        & (df["ride_length_minutes"] < COMMUTE_MAX_MINUTES)
    )
    return df


def headline_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Headline numbers per rider type; df must have the analysis fields."""
    grouped = df.groupby("member_casual", observed=True)
    out = pd.DataFrame(
        {
            "rides": grouped.size(),
            "median_min": grouped["ride_length_minutes"].median().round(2),
            "weekend_share": (grouped["is_weekend"].mean() * 100).round(2),
            "electric_share": (grouped["electric"].mean() * 100).round(2),
            "summer_rides": grouped["summer"].sum().astype(int),
            "commute_like_rides": grouped["commute_like"].sum().astype(int),
        }
    )
    return out.reindex(RIDER_ORDER)


def _share_within(df: pd.DataFrame, group: list[str], keys: list[str]) -> pd.Series:
    """Rides per group as a percentage of the rides in the same keys."""
    counts = df.groupby(group, observed=True).size().rename("rides")
    totals = counts.groupby(level=keys, observed=True).transform("sum")
    return counts / totals * 100


def hourly_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Share of each rider type's weekday (or weekend) rides by start hour."""
    keys = ["member_casual", "day_type"]
    share = _share_within(df, keys + ["hour"], keys)
    return share.rename("share_pct").reset_index()


def weekday_hour_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Share of each rider type's rides by weekday and start hour."""
    df = df.assign(day_of_week=df["day_of_week"].astype(str))
    share = _share_within(
        df, ["member_casual", "day_of_week", "hour"], ["member_casual"]
    )
    return share.rename("share_pct").reset_index()


def monthly_rides(df: pd.DataFrame) -> pd.DataFrame:
    """Rides per analysis month and rider type, plus the casual share (%)."""
    monthly = (
        df.groupby(["analysis_month", "member_casual"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=RIDER_ORDER, fill_value=0)
    )
    monthly["casual_share_pct"] = (
        monthly["casual"] / (monthly["casual"] + monthly["member"]) * 100
    )
    return monthly


def duration_bucket_shares(df: pd.DataFrame) -> pd.DataFrame:
    """Share of each rider type's rides in each duration bucket."""
    share = _share_within(
        df, ["member_casual", "duration_bucket"], ["member_casual"]
    )
    return share.rename("share_pct").reset_index()


def top_casual_stations(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """The n start stations with most casual rides and their casual share.

    Rides without a start station are left out; stations are identified by
    start_station_id and shown with their first station name.
    """
    stations = df[df["start_station_id"].notna()]
    is_casual = stations["member_casual"].astype(str).eq("casual")
    by_station = (
        stations.assign(casual=is_casual)
        .groupby("start_station_id", observed=True)
        .agg(
            name=("start_station_name", "first"),
            casual=("casual", "sum"),
            total=("casual", "size"),
        )
    )
    by_station["casual_share_pct"] = by_station["casual"] / by_station["total"] * 100
    return by_station.sort_values("casual", ascending=False).head(n)


def behaviour_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Percent of each rider type's rides that are weekend, summer,
    commute-like or electric."""
    grouped = df.groupby("member_casual", observed=True)
    profile = pd.DataFrame(
        {
            "Weekend rides": grouped["is_weekend"].mean() * 100,
            "Summer (Jun-Aug)": grouped["summer"].mean() * 100,
            "Commute-like weekday": grouped["commute_like"].mean() * 100,
            "Electric bike": grouped["electric"].mean() * 100,
        }
    )
    return profile.reindex(RIDER_ORDER)
