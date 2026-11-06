from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"


# ---------------------------------------------------------
# Find CSV files
# ---------------------------------------------------------

csv_files = sorted(DATA_FOLDER.glob("*.csv"))

if len(csv_files) != 12:
    print(f"WARNING: Expected 12 CSV files, found {len(csv_files)}")


# ---------------------------------------------------------
# Read schemas
# ---------------------------------------------------------

schemas = {}

for file_path in csv_files:

    df_sample = pd.read_csv(
        file_path,
        nrows=5
    )

    schemas[file_path.name] = {
        "columns": list(df_sample.columns),
        "column_count": len(df_sample.columns),
        "dtypes": df_sample.dtypes.astype(str).to_dict()
    }


# ---------------------------------------------------------
# Compare all schemas to the first file
# ---------------------------------------------------------

reference_file = csv_files[0]
reference_schema = schemas[reference_file.name]

print("=" * 100)
print("SCHEMA CONSISTENCY CHECK")
print("=" * 100)

print(f"\nReference file: {reference_file.name}")
print(f"Reference column count: {reference_schema['column_count']}")

print("\nReference columns:")
for i, column in enumerate(reference_schema["columns"], start=1):
    print(f"{i:2}. {column}")


# ---------------------------------------------------------
# Compare each file
# ---------------------------------------------------------

all_columns_match = True

for file_name, schema in schemas.items():

    columns_match = (
        schema["columns"] == reference_schema["columns"]
    )

    count_match = (
        schema["column_count"]
        == reference_schema["column_count"]
    )

    if columns_match and count_match:
        status = "MATCH"
    else:
        status = "DIFFERENT"
        all_columns_match = False

    print(
        f"\n{file_name:<35} "
        f"Columns: {schema['column_count']:>2} "
        f"Status: {status}"
    )

    if not columns_match:

        reference_columns = set(reference_schema["columns"])
        current_columns = set(schema["columns"])

        missing = reference_columns - current_columns
        extra = current_columns - reference_columns

        if missing:
            print(f"  Missing columns: {sorted(missing)}")

        if extra:
            print(f"  Extra columns: {sorted(extra)}")


# ---------------------------------------------------------
# Compare data types
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("DATA TYPE CHECK")
print("=" * 100)

for file_name, schema in schemas.items():

    differences = []

    for column in reference_schema["columns"]:

        reference_type = reference_schema["dtypes"].get(column)
        current_type = schema["dtypes"].get(column)

        if reference_type != current_type:

            differences.append(
                f"{column}: {reference_type} -> {current_type}"
            )

    if differences:

        print(f"\n{file_name}")
        for difference in differences:
            print(f"  {difference}")

    else:
        print(f"{file_name:<35} All sampled data types match")


# ---------------------------------------------------------
# Final conclusion
# ---------------------------------------------------------

print("\n" + "=" * 100)

if all_columns_match:
    print("RESULT: All files have the same column structure.")
else:
    print("RESULT: Schema differences detected. Investigation required.")

print("=" * 100)