"""Load the clean Cyclistic table into PostgreSQL.

Steps: create the table from sql/00_schema.sql (this replaces any old
copy), stream cyclistic_clean.csv into it with COPY, then check that the
row count in the database equals the number of data rows in the file.

COPY is PostgreSQL's bulk-load command. It is much faster than inserting
row by row, because the server reads the whole stream in one operation.

Connection: set CYCLISTIC_DSN, for example
"host=localhost dbname=cyclistic user=postgres", and set the password in
PGPASSWORD. Run with: python -m cyclistic.load_to_postgres
"""

import os
from pathlib import Path

import psycopg
from tqdm import tqdm

from cyclistic import config

COPY_SQL = "COPY cyclistic_clean FROM STDIN WITH (FORMAT csv, HEADER true)"
READ_BYTES = 1024 * 1024


def get_dsn() -> str:
    return os.environ.get("CYCLISTIC_DSN", config.POSTGRES_DSN_DEFAULT)


def create_table(conn: psycopg.Connection, schema_file: Path) -> None:
    conn.execute(schema_file.read_text(encoding="utf-8"))


def copy_csv(conn: psycopg.Connection, csv_file: Path) -> None:
    """Stream the CSV into cyclistic_clean with COPY, showing progress."""
    total = csv_file.stat().st_size
    with conn.cursor() as cur, csv_file.open("rb") as f, tqdm(
        total=total, unit="B", unit_scale=True, desc="Loading"
    ) as bar:
        with cur.copy(COPY_SQL) as copy:
            while chunk := f.read(READ_BYTES):
                copy.write(chunk)
                bar.update(len(chunk))


def count_csv_rows(csv_file: Path) -> int:
    """Count data rows (lines minus the header). Rides have no embedded
    line breaks, so one line is one ride."""
    with csv_file.open("rb") as f:
        return sum(1 for _ in f) - 1


def main() -> None:
    expected = count_csv_rows(config.CLEAN_FILE)
    with psycopg.connect(get_dsn()) as conn:
        create_table(conn, config.SCHEMA_FILE)
        copy_csv(conn, config.CLEAN_FILE)
        loaded = conn.execute("SELECT COUNT(*) FROM cyclistic_clean").fetchone()[0]
        conn.execute("ANALYZE cyclistic_clean")
    print(f"Rows in CSV: {expected:,}   Rows in PostgreSQL: {loaded:,}")
    if loaded != expected or loaded != config.EXPECTED_CLEAN_ROWS:
        raise SystemExit("Row count check FAILED")
    print("Row count check PASSED")


if __name__ == "__main__":
    main()
