"""Reconcile pandas results with live PostgreSQL results.

The same headline metrics are computed twice, by independent code: once in
pandas (cyclistic.analysis) from cyclistic_clean.csv and once in PostgreSQL
from the cyclistic_clean table. If they differ, one of them is wrong.

Slow test (reads 1.6 GB and queries PostgreSQL). It runs only when
CYCLISTIC_FULL_TESTS=1, the clean file exists and the database answers.
Set CYCLISTIC_DSN and PGPASSWORD first (see cyclistic.load_to_postgres).

Run with: python -m pytest tests/test_reconcile_sql.py -v
"""

import os

import pandas as pd
import psycopg
import pytest

from cyclistic import config
from cyclistic.analysis import add_analysis_fields, headline_metrics, load_clean
from cyclistic.load_to_postgres import get_dsn

SQL = """
SELECT
    member_casual,
    COUNT(*)                                                       AS rides,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP
          (ORDER BY ride_length_minutes)::numeric, 2)              AS median_min,
    ROUND((100.0 * AVG((day_of_week IN ('Saturday', 'Sunday'))::int))::numeric, 2)
                                                                   AS weekend_share,
    ROUND((100.0 * AVG((rideable_type = 'electric_bike')::int))::numeric, 2)
                                                                   AS electric_share,
    COUNT(*) FILTER (WHERE SUBSTRING(source_file, 5, 2) IN ('06', '07', '08'))
                                                                   AS summer_rides,
    COUNT(*) FILTER (
        WHERE day_of_week NOT IN ('Saturday', 'Sunday')
          AND (EXTRACT(HOUR FROM started_at) BETWEEN 6 AND 9
               OR EXTRACT(HOUR FROM started_at) BETWEEN 16 AND 19)
          AND ride_length_minutes < 30
    )                                                              AS commute_like_rides
FROM cyclistic_clean
GROUP BY member_casual
"""


@pytest.mark.skipif(
    os.environ.get("CYCLISTIC_FULL_TESTS") != "1" or not config.CLEAN_FILE.exists(),
    reason="full-data test: set CYCLISTIC_FULL_TESTS=1 and build the clean file",
)
def test_pandas_matches_postgresql():
    try:
        conn = psycopg.connect(get_dsn())
    except psycopg.OperationalError as error:
        pytest.skip(f"PostgreSQL not reachable: {error}")
    with conn:
        rows = conn.execute(SQL).fetchall()
        columns = [c.name for c in conn.execute(SQL).description]
    sql_metrics = (
        pd.DataFrame(rows, columns=columns)
        .set_index("member_casual")
        .astype(float)
        .reindex(["member", "casual"])
    )

    pandas_metrics = headline_metrics(add_analysis_fields(load_clean())).astype(float)

    pd.testing.assert_frame_equal(
        pandas_metrics[sql_metrics.columns],
        sql_metrics,
        check_names=False,
        check_dtype=False,
        atol=0.011,
    )
