from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "01_Project_Management"
    / "missing_values_inventory.csv"
)


# ---------------------------------------------------------
# Find CSV files
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in {DATA_FOLDER}"
    )


# ---------------------------------------------------------
# Check missing values
# ---------------------------------------------------------

results = []

for file_path in csv_files:

    print(f"Checking: {file_path.name}")

    missing_counts = {}
    total_rows = 0

    for chunk in pd.read_csv(
        file_path,
        chunksize=100_000
    ):

        total_rows += len(chunk)

        chunk_missing = chunk.isna().sum()

        for column, count in chunk_missing.items():

            missing_counts[column] = (
                missing_counts.get(column, 0) + count
            )

    for column, missing_count in missing_counts.items():

        missing_pct = (
            missing_count / total_rows * 100
            if total_rows > 0
            else 0
        )

        results.append({
            "file_name": file_path.name,
            "row_count": total_rows,
            "column_name": column,
            "missing_count": int(missing_count),
            "missing_percentage": round(missing_pct, 4)
        })


# ---------------------------------------------------------
# Create output
# ---------------------------------------------------------

results_df = pd.DataFrame(results)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Display pivot table
# ---------------------------------------------------------

pivot = results_df.pivot(
    index="column_name",
    columns="file_name",
    values="missing_percentage"
)

print("\n" + "=" * 100)
print("MISSING VALUE PERCENTAGE BY COLUMN")
print("=" * 100)

print(pivot.to_string())

print("\n" + "=" * 100)
print("TOTAL MISSING VALUES BY COLUMN")
print("=" * 100)

summary = (
    results_df
    .groupby("column_name")
    .agg(
        total_missing=("missing_count", "sum"),
        total_rows=("row_count", "sum")
    )
)

summary["missing_percentage"] = (
    summary["total_missing"]
    / summary["total_rows"]
    * 100
)

summary = summary.sort_values(
    "missing_percentage",
    ascending=False
)

print(summary.to_string())

print("\nInventory saved to:")
print(OUTPUT_FILE.resolve())