"""Tests for the chart tables and the chart files.

Each test builds a small table of rides and checks one rule:
- hourly and weekday-by-hour shares add up to 100% for each rider type;
- the casual share by month is casual rides divided by all rides;
- duration buckets put 14.99 minutes below 15 and exactly 15 and 60 in the
  next bucket up;
- the station ranking leaves out rides with no start station and sorts by
  casual rides;
- make_all draws all six charts to PNG files, and none of them is empty.

Run with: python -m pytest -v
"""

import numpy as np
import pandas as pd
import pytest

from cyclistic import analysis, plot_charts


def rides_from(rows):
    """rows: dicts with started_at, minutes, rider, bike, month, station."""
    df = pd.DataFrame(
        {
            "started_at": pd.to_datetime([r["started_at"] for r in rows]),
            "ride_length_minutes": [r["minutes"] for r in rows],
            "member_casual": [r["rider"] for r in rows],
            "rideable_type": [r.get("bike", "classic_bike") for r in rows],
            "source_file": [f"{r['month']}-divvy-tripdata.csv" for r in rows],
            "start_station_id": [r.get("station") for r in rows],
            "start_station_name": [r.get("station") for r in rows],
        }
    )
    df["day_of_week"] = df["started_at"].dt.day_name()
    return analysis.add_analysis_fields(df)


def random_rides(n=3000, seed=1):
    rng = np.random.default_rng(seed)
    starts = pd.Timestamp("2026-01-01") + pd.to_timedelta(
        rng.integers(0, 60 * 24 * 150, n), unit="m"
    )
    months = [f"2026{m:02d}" for m in starts.month]
    riders = rng.choice(["member", "casual"], n)
    stations = rng.choice(["Navy Pier", "Shedd Aquarium", "Clark St", None], n)
    return rides_from(
        [
            {
                "started_at": s, "minutes": float(m), "rider": r, "month": mo,
                "station": st, "bike": b,
            }
            for s, m, r, mo, st, b in zip(
                starts,
                rng.gamma(2, 8, n),
                riders,
                months,
                stations,
                rng.choice(["classic_bike", "electric_bike"], n),
            )
        ]
    )


def test_hourly_profile_shares_sum_to_100():
    out = analysis.hourly_profile(random_rides())
    sums = out.groupby(["member_casual", "day_type"], observed=True)["share_pct"].sum()
    assert sums.to_numpy() == pytest.approx(100)


def test_heatmap_shares_sum_to_100_per_rider():
    out = analysis.weekday_hour_heatmap(random_rides())
    sums = out.groupby("member_casual", observed=True)["share_pct"].sum()
    assert sums.to_numpy() == pytest.approx(100)


def test_monthly_casual_share():
    rows = [
        {"started_at": "2026-01-05 10:00", "minutes": 5, "rider": "casual", "month": "202601"},
        {"started_at": "2026-01-06 10:00", "minutes": 5, "rider": "member", "month": "202601"},
        {"started_at": "2026-01-07 10:00", "minutes": 5, "rider": "member", "month": "202601"},
        {"started_at": "2026-01-08 10:00", "minutes": 5, "rider": "member", "month": "202601"},
    ]
    out = analysis.monthly_rides(rides_from(rows))
    assert out.loc["202601", "casual"] == 1
    assert out.loc["202601", "member"] == 3
    assert out.loc["202601", "casual_share_pct"] == pytest.approx(25)


def test_duration_bucket_edges():
    minutes = [14.99, 15, 29.99, 30, 59.99, 60]
    rows = [
        {"started_at": "2026-01-05 10:00", "minutes": m, "rider": "member", "month": "202601"}
        for m in minutes
    ]
    out = rides_from(rows)
    assert list(out["duration_bucket"].astype(str)) == [
        "<15 min", "15-29 min", "15-29 min", "30-59 min", "30-59 min", "60+ min",
    ]


def test_top_casual_stations_ignores_missing_and_sorts():
    def ride(rider, station):
        return {"started_at": "2026-01-05 10:00", "minutes": 5, "rider": rider,
                "month": "202601", "station": station}

    rows = (
        [ride("casual", "A")] * 3
        + [ride("member", "A")] * 1
        + [ride("casual", "B")] * 5
        + [ride("casual", None)] * 10
    )
    top = analysis.top_casual_stations(rides_from(rows), n=5)
    assert list(top["name"]) == ["B", "A"]
    assert list(top["casual"]) == [5, 3]
    assert top.loc["A", "casual_share_pct"] == pytest.approx(75)


def test_behaviour_profile_order_and_columns():
    profile = analysis.behaviour_profile(random_rides())
    assert list(profile.index) == ["member", "casual"]
    assert list(profile.columns) == [
        "Weekend rides", "Summer (Jun-Aug)", "Commute-like weekday", "Electric bike",
    ]
    assert ((profile >= 0) & (profile <= 100)).all().all()


def test_make_all_writes_six_nonempty_pngs(tmp_path):
    saved = plot_charts.make_all(random_rides(), tmp_path)
    assert len(saved) == 6
    for path in saved:
        assert path.suffix == ".png"
        assert path.stat().st_size > 5_000
