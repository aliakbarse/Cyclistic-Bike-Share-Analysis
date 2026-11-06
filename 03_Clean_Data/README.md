# Clean data (not versioned)

`cyclistic_clean.csv` (6,115,947 rows, about 1.6 GB) is generated, not stored here.

**To rebuild**
1. Place the extracted raw CSVs in `02_Raw_Data/extracted/` (see that folder's README).
2. In `06_Python/16_clean_cyclistic_data.py`, set `DATA_DIR`, `OUTPUT_DIR` and `DUPLICATE_FILE` to your local paths.
3. Run `python 06_Python/16_clean_cyclistic_data.py`, then `python 06_Python/17_validate_clean_data.py`. The validator expects 6,115,947 rows, no duplicate ride IDs and no negative durations.
