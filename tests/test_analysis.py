"""Tests for the analysis definitions in cyclistic.analysis.

Each test builds a few rides and checks one definition:
- a weekday ride in the morning window and under 30 minutes is commute-like,
  and a ride at the window edge hours (06:xx and 19:xx) is included;
- weekend rides, rides outside the windows and rides of 30 minutes or more
  are not commute-like;
- the season comes from the source file name, not from started_at, so a ride
  that crosses midnight at the end of a month stays in its file's month;
- headline_metrics returns members first and the right shares.

Run with: python -m pytest -v
"""

import pandas as pd
import pytest

from cyclistic.analysis import add_analysis_fields, headline_metrics


def make_rides(rows):
    """rows: (started_at, day_of_week, minutes, rider, bike, source_file)."""
    return pd.DataFrame(
        {
            "started_at": pd.to_datetime([r[0] for r in rows]),
            "day_of_week": [r[1] for r in rows],
            "ride_length_minutes": [r[2] for r in rows],
            "member_casual": [r[3] for r in rows],
            "rideable_type": [r[4] for r in rows],
            "source_file": [r[5] for r in rows],
        }
    )


def commute_flags(rows):
    return list(add_analysis_fields(make_rides(rows))["commute_like"])


def test_commute_like_rule():
    rows = [
        ("2026-03-02 08:15", "Monday", 12, "member", "classic_bike", "202603-x.csv"),
        ("2026-03-02 06:00", "Monday", 12, "member", "classic_bike", "202603-x.csv"),
        ("2026-03-02 19:59", "Monday", 12, "member", "classic_bike", "202603-x.csv"),
        ("2026-03-02 20:00", "Monday", 12, "member", "classic_bike", "202603-x.csv"),
        ("2026-03-02 12:00", "Monday", 12, "member", "classic_bike", "202603-x.csv"),
        ("2026-03-07 08:15", "Saturday", 12, "casual", "classic_bike", "202603-x.csv"),
        ("2026-03-02 08:15", "Monday", 30, "casual", "classic_bike", "202603-x.csv"),
        ("2026-03-02 08:15", "Monday", 29.9, "casual", "classic_bike", "202603-x.csv"),
    ]
    assert commute_flags(rows) == [True, True, True, False, False, False, False, True]


def test_season_comes_from_source_file_not_start_time():
    rows = [
        ("2026-06-30 23:55", "Tuesday", 20, "casual", "classic_bike", "202606-x.csv"),
        ("2026-07-01 00:05", "Wednesday", 20, "casual", "classic_bike", "202606-x.csv"),
        ("2026-09-15 10:00", "Tuesday", 20, "member", "classic_bike", "202609-x.csv"),
    ]
    out = add_analysis_fields(make_rides(rows))
    assert list(out["season"]) == ["Summer", "Summer", "Autumn"]
    assert list(out["summer"]) == [True, True, False]


def test_add_analysis_fields_does_not_change_input():
    df = make_rides(
        [("2026-03-02 08:15", "Monday", 12, "member", "classic_bike", "202603-x.csv")]
    )
    before = df.copy()
    add_analysis_fields(df)
    pd.testing.assert_frame_equal(df, before)


def test_headline_metrics():
    rows = [
        ("2026-07-04 10:00", "Saturday", 10, "casual", "electric_bike", "202607-x.csv"),
        ("2026-07-06 08:00", "Monday", 20, "casual", "classic_bike", "202607-x.csv"),
        ("2026-01-05 08:00", "Monday", 6, "member", "classic_bike", "202601-x.csv"),
        ("2026-01-06 17:00", "Tuesday", 8, "member", "classic_bike", "202601-x.csv"),
        ("2026-01-10 11:00", "Saturday", 40, "member", "electric_bike", "202601-x.csv"),
    ]
    m = headline_metrics(add_analysis_fields(make_rides(rows)))

    assert list(m.index) == ["member", "casual"]
    assert m.loc["member", "rides"] == 3
    assert m.loc["casual", "rides"] == 2
    assert m.loc["member", "median_min"] == pytest.approx(8)
    assert m.loc["casual", "median_min"] == pytest.approx(15)
    assert m.loc["member", "weekend_share"] == pytest.approx(33.33)
    assert m.loc["casual", "weekend_share"] == pytest.approx(50)
    assert m.loc["member", "electric_share"] == pytest.approx(33.33)
    assert m.loc["casual", "summer_rides"] == 2
    assert m.loc["member", "summer_rides"] == 0
    assert m.loc["member", "commute_like_rides"] == 2
    assert m.loc["casual", "commute_like_rides"] == 1
