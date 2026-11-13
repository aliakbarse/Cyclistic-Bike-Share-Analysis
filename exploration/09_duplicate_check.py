from pathlib import Path
import sqlite3
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"

TEMP_DB = PROJECT_ROOT / "06_Python" / ".duplicate_check.sqlite"


# ---------------------------------------------------------
# Create temporary SQLite database
# ---------------------------------------------------------

if TEMP_DB.exists():
    TEMP_DB.unlink()

conn = sqlite3.connect(TEMP_DB)

conn.execute("""
    CREATE TABLE ride_ids (
        ride_id TEXT PRIMARY KEY,
        first_file TEXT NOT NULL
    )
""")

conn.commit()


# ---------------------------------------------------------
# Variables for results
# ---------------------------------------------------------

total_rows = 0
null_ride_ids = 0
duplicate_ids = 0

monthly_results = []


# ---------------------------------------------------------
# Process files
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

for file_path in csv_files:

    print(f"Checking: {file_path.name}")

    file_rows = 0
    file_null_ids = 0
    file_duplicate_ids = 0

    for chunk in pd.read_csv(
        file_path,
        usecols=["ride_id"],
        dtype="string",
        chunksize=100_000
    ):

        file_rows += len(chunk)
        total_rows += len(chunk)

        # -------------------------------------------------
        # Null ride IDs
        # -------------------------------------------------

        null_mask = chunk["ride_id"].isna()

        null_count = null_mask.sum()

        file_null_ids += null_count
        null_ride_ids += null_count

        # Ignore null IDs for duplicate testing
        valid_ids = chunk.loc[
            ~null_mask,
            "ride_id"
        ]

        # -------------------------------------------------
        # Duplicates within this chunk
        # -------------------------------------------------

        duplicate_in_chunk = (
            valid_ids.duplicated(keep="first").sum()
        )

        # -------------------------------------------------
        # Insert into SQLite
        # -------------------------------------------------

        rows_to_insert = [
            (ride_id, file_path.name)
            for ride_id in valid_ids
        ]

        before_changes = conn.total_changes

        conn.executemany(
            """
            INSERT OR IGNORE INTO ride_ids
            (ride_id, first_file)
            VALUES (?, ?)
            """,
            rows_to_insert
        )

        conn.commit()

        new_rows = (
            conn.total_changes
            - before_changes
        )

        duplicate_count = (
            len(valid_ids)
            - new_rows
        )

        file_duplicate_ids += duplicate_count
        duplicate_ids += duplicate_count

    monthly_results.append({
        "file_name": file_path.name,
        "rows": file_rows,
        "null_ride_ids": file_null_ids,
        "duplicate_ride_ids": file_duplicate_ids
    })


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("DUPLICATE RIDE ID CHECK")
print("=" * 100)

results_df = pd.DataFrame(monthly_results)

print(
    results_df.to_string(index=False)
)


print("\n" + "=" * 100)
print("OVERALL RESULTS")
print("=" * 100)

print(f"Total rows:             {total_rows:,}")
print(f"Null ride IDs:          {null_ride_ids:,}")
print(f"Duplicate ride IDs:     {duplicate_ids:,}")


# ---------------------------------------------------------
# Cross-file duplicate count
# ---------------------------------------------------------

duplicate_cross_file = conn.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT ride_id
        FROM ride_ids
        GROUP BY ride_id
        HAVING COUNT(*) > 1
    )
""").fetchone()[0]

# The table uses PRIMARY KEY, so this should normally be zero.
# The main duplicate count above captures records that were
# rejected as already existing.
# This additional query is retained as a structural check.

print(
    f"Distinct ride IDs stored: "
    f"{conn.execute('SELECT COUNT(*) FROM ride_ids').fetchone()[0]:,}"
)

print("\nTemporary duplicate-check database:")
print(TEMP_DB)


# ---------------------------------------------------------
# Close and remove temporary database
# ---------------------------------------------------------

conn.close()

if TEMP_DB.exists():
    TEMP_DB.unlink()

print("\nTemporary database deleted.")