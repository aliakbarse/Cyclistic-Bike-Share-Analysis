from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"
OUTPUT_FILE = PROJECT_ROOT / "01_Project_Management" / "data_inventory.csv"


# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------

def find_column(columns, candidates):
    """
    Return the first matching column name from a list of candidates.
    Matching is case-insensitive.
    """
    column_map = {col.lower(): col for col in columns}

    for candidate in candidates:
        if candidate.lower() in column_map:
            return column_map[candidate.lower()]

    return None


# ---------------------------------------------------------
# Find CSV files
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in: {DATA_FOLDER.resolve()}"
    )

print(f"Found {len(csv_files)} CSV files.\n")


# ---------------------------------------------------------
# Inspect each file
# ---------------------------------------------------------

inventory = []

for file_path in csv_files:

    print(f"Inspecting: {file_path.name}")

    # Read only the header first
    sample = pd.read_csv(file_path, nrows=5)

    columns = list(sample.columns)

    # Try to identify important fields
    started_col = find_column(
        columns,
        ["started_at", "start_time", "started"]
    )

    ended_col = find_column(
        columns,
        ["ended_at", "end_time", "ended"]
    )

    member_col = find_column(
        columns,
        ["member_casual", "member_type", "customer_type"]
    )

    # -----------------------------------------------------
    # Process file in chunks
    # -----------------------------------------------------

    total_rows = 0
    min_date = None
    max_date = None
    member_values = set()

    for chunk in pd.read_csv(file_path, chunksize=100_000):

        total_rows += len(chunk)

        # Date range
        if started_col and started_col in chunk.columns:

            dates = pd.to_datetime(
                chunk[started_col],
                errors="coerce"
            )

            chunk_min = dates.min()
            chunk_max = dates.max()

            if pd.notna(chunk_min):
                min_date = (
                    chunk_min
                    if min_date is None
                    else min(min_date, chunk_min)
                )

            if pd.notna(chunk_max):
                max_date = (
                    chunk_max
                    if max_date is None
                    else max(max_date, chunk_max)
                )

        # Membership values
        if member_col and member_col in chunk.columns:
            member_values.update(
                chunk[member_col]
                .dropna()
                .astype(str)
                .unique()
            )

    # -----------------------------------------------------
    # Store results
    # -----------------------------------------------------

    inventory.append({
        "file_name": file_path.name,
        "file_size_mb": round(file_path.stat().st_size / (1024 ** 2), 2),
        "row_count": total_rows,
        "column_count": len(columns),
        "started_column": started_col,
        "ended_column": ended_col,
        "membership_column": member_col,
        "min_started_at": min_date,
        "max_started_at": max_date,
        "membership_values": ", ".join(sorted(member_values)),
        "columns": ", ".join(columns)
    })


# ---------------------------------------------------------
# Create inventory dataframe
# ---------------------------------------------------------

inventory_df = pd.DataFrame(inventory)

# Sort by filename
inventory_df = inventory_df.sort_values("file_name")

# Save
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

inventory_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

print("\n" + "=" * 100)
print("DATA INVENTORY")
print("=" * 100)

print(inventory_df[
    [
        "file_name",
        "file_size_mb",
        "row_count",
        "column_count",
        "min_started_at",
        "max_started_at",
        "membership_values"
    ]
].to_string(index=False))

print("\nInventory saved to:")
print(OUTPUT_FILE.resolve())