# Clean data (not versioned)

`cyclistic_clean.csv` (6,115,947 rows, about 1.6 GB) is generated, not stored here.

**To rebuild**
1. Place the extracted raw CSVs in `02_Raw_Data/extracted/` (see that folder's README).
2. Install the project: `python -m pip install -e ".[dev]"`
3. Run `python -m cyclistic.run_pipeline`. It cleans the raw files, writes `cyclistic_clean.csv` here, and then validates it: 6,115,947 rows, no duplicate ride IDs and no negative durations.

Paths are set in `src/cyclistic/config.py` and are relative to the repository, so nothing needs editing.
