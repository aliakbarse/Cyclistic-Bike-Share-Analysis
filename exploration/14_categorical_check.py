from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "02_Raw_Data" / "extracted"


# Expected values from the case structure
expected_membership = {"casual", "member"}

expected_bike_types = {
    "classic_bike",
    "electric_bike"
}


membership_values = set()
bike_values = set()

membership_counts = {}
bike_counts = {}

blank_membership = 0
blank_bike_type = 0


csv_files = sorted(DATA_FOLDER.glob("*.csv"))

for file_path in csv_files:

    print(f"Checking: {file_path.name}")

    for chunk in pd.read_csv(
        file_path,
        usecols=[
            "member_casual",
            "rideable_type"
        ],
        dtype="string",
        chunksize=100_000
    ):

        # -------------------------------------------------
        # Strip whitespace for inspection only
        # -------------------------------------------------

        membership = (
            chunk["member_casual"]
            .str.strip()
        )

        bike_type = (
            chunk["rideable_type"]
            .str.strip()
        )

        # Blank strings
        blank_membership += (
            membership.fillna("").eq("")
        ).sum()

        blank_bike_type += (
            bike_type.fillna("").eq("")
        ).sum()

        # Unique values
        membership_values.update(
            membership.dropna().unique()
        )

        bike_values.update(
            bike_type.dropna().unique()
        )

        # Counts
        for value, count in membership.value_counts(
            dropna=False
        ).items():

            membership_counts[value] = (
                membership_counts.get(value, 0) + count
            )

        for value, count in bike_type.value_counts(
            dropna=False
        ).items():

            bike_counts[value] = (
                bike_counts.get(value, 0) + count
            )


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

print("\n" + "=" * 100)
print("MEMBERSHIP VALUES")
print("=" * 100)

for value in sorted(membership_values):
    print(
        f"{repr(value):<25} "
        f"{membership_counts.get(value, 0):>12,}"
    )

print(f"\nBlank membership values: {blank_membership:,}")

print("\n" + "=" * 100)
print("BIKE TYPE VALUES")
print("=" * 100)

for value in sorted(bike_values):
    print(
        f"{repr(value):<25} "
        f"{bike_counts.get(value, 0):>12,}"
    )

print(f"\nBlank bike-type values: {blank_bike_type:,}")


# ---------------------------------------------------------
# Unexpected values
# ---------------------------------------------------------

unexpected_membership = (
    membership_values - expected_membership
)

unexpected_bike_types = (
    bike_values - expected_bike_types
)

print("\n" + "=" * 100)
print("EXPECTED-VALUE CHECK")
print("=" * 100)

print(
    f"Unexpected membership values: "
    f"{unexpected_membership if unexpected_membership else 'None'}"
)

print(
    f"Unexpected bike-type values: "
    f"{unexpected_bike_types if unexpected_bike_types else 'None'}"
)