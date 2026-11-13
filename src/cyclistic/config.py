"""Shared paths and settings for the Cyclistic pipeline.

Defines the project folders (raw data, clean data and documentation), the
name of the clean output file, the expected clean row count, the allowed
category values and the daylight-saving (DST) date that needs a duration
correction. Every other module imports these values, so each setting is
defined in one place and no path depends on one person's computer.
"""

from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "02_Raw_Data" / "extracted"
CLEAN_DIR = PROJECT_ROOT / "03_Clean_Data"
CLEAN_FILE = CLEAN_DIR / "cyclistic_clean.csv"

DUPLICATE_FILE = (
    PROJECT_ROOT
    / "docs"
    / "project_management"
    / "cross_file_duplicate_investigation.csv"
)

# 12 monthly files, September 2025 to August 2026.
EXPECTED_RAW_FILES = 12
EXPECTED_CLEAN_ROWS = 6_115_947

MEMBERSHIP_VALUES = frozenset({"casual", "member"})
BIKE_TYPE_VALUES = frozenset({"classic_bike", "electric_bike"})

# On this date the clocks went back one hour (US daylight-saving end), so
# some rides appear to end before they start. See docs/project_management.
DST_FALLBACK_DATE = date(2025, 11, 2)
DST_CORRECTION_MINUTES = 60

CHUNK_SIZE = 100_000
