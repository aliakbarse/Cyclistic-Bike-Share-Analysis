# Cyclistic Bike-Share Analysis

## Executive Summary

Cyclistic wants more annual members. This project analyses 6.1 million bike-share rides (September 2025 - August 2026) to find how casual riders differ from annual members and where casual riders look most like members.

Casual riders are seasonal and weekend-leaning; members are year-round weekday commuters. The groups overlap more than they differ: about 28% of casual rides already follow the member pattern (weekday, commute hours, under 30 minutes), and casual riding grows sharply every spring.

## Business Problem

Increase the number of annual memberships by converting more casual riders into members.

**Business task:** analyse how annual members and casual riders use Cyclistic bikes differently, to identify opportunities for conversion.

**Key questions**
1. How do annual members and casual riders use Cyclistic bikes differently?
2. Why would casual riders buy annual memberships?
3. How can Cyclistic use digital media to influence casual riders to become members?

## Key Findings

1. **Different rhythms.** Members have a sharp weekday morning peak (20% of rides start 06:00-09:59 vs 11% for casual); 37% of casual rides fall on weekends vs 23% for members.
2. **Casual riding is far more seasonal.** 47% of casual rides happen in June-August (members: 38%). Casual share of all rides ranges from 18% in January to 41% in July.
3. **Casual rides run longer.** Median 10.9 min vs 8.6 min for members (1.27x). The gap in the mean is larger (1.67x) because a few very long rides inflate it; it is 1.46x after trimming rides under 1 minute and over 3 hours.
4. **Casual riders ride from lakefront and tourist stations, but are dispersed.** They are the majority at stations such as Shedd Aquarium (82%) and Navy Pier (76%), yet the ten busiest casual stations hold only about 10% of casual rides.
5. **Bike type is not the differentiator.** Electric-bike share is 74% for casual riders vs 68% for members.

## Recommendations

1. **Prioritise commute-like casual riders** (about 602,000 rides, 28% of casual rides) for membership messaging; they are the closest behavioural match to members.
2. **Run campaigns April-June.** Casual rides rise 86% from April to May (members: 29%), so the reachable pool grows fastest then.
3. **Lead with in-app and email; use stations as a supporting channel.** The top 15 casual stations hold only about 12% of casual rides.
4. **Test before scaling.** Use Cyclistic's rider-level data to measure ride frequency and price break-even, and split-test an offer against a control group.

Full detail: [`09_Reports/Cyclistic_Findings_Report.md`](09_Reports/Cyclistic_Findings_Report.md)

## Data

Cyclistic historical trip data (Divvy), provided for the Google Data Analytics Capstone case study.

- 12 monthly files, September 2025 - August 2026
- 6,115,982 raw records, 13 columns; 6,115,947 after cleaning (35 cross-file duplicates removed)
- 29 negative durations at the 2 Nov 2025 daylight-saving change flagged and corrected
- Raw files are never modified; all cleaning is scripted

## Methodology

Ask → Prepare → Process → Analyze → Share → Act

| Phase | Where |
|---|---|
| Ask | `01_Project_Management/01_Ask.md` |
| Prepare | `01_Project_Management/02-06_*.md`, `06_Python/00-15_*.py` |
| Process | `01_Project_Management/07_Process_Cleaning_Plan.md`, `06_Python/16-17_*.py` |
| Analyze | `05_SQL/`, `06_Python/cyclistic_analysis.ipynb`, `04_Excel/` |
| Share | `09_Reports/`, `07_PowerBI/` (dashboard in progress) |

**Verification:** headline metrics were computed independently in SQL and pandas and reconcile exactly (see the notebook, section 2).

## Tools

Excel | PostgreSQL | Power BI | Python

## Dashboard

*Power BI dashboard in progress. Screenshots will be added to `08_Visualizations/`.*

Analysis charts (Python): `08_Visualizations/analysis_charts/`

## Project Structure

```
01_Cyclistic_Bike_Share/
├── 01_Project_Management/   Ask, data inventory, dictionary, ROCCC, limitations, cleaning plan
├── 02_Raw_Data/             Original monthly zips (unmodified)
├── 03_Clean_Data/           cyclistic_clean.csv (output of 16_clean_cyclistic_data.py)
├── 04_Excel/                data_dictionary, exploratory_analysis, summary_tables
├── 05_SQL/                  01 validation, 02 exploration, 03 deep analysis, 04 final queries
├── 06_Python/               00-17 checks and cleaning scripts, cyclistic_analysis.ipynb
├── 07_PowerBI/              Power BI report
├── 08_Visualizations/       Dashboard exports and analysis_charts/
└── 09_Reports/              Cyclistic_Findings_Report.md
```

## Limitations

- **Rides are not riders.** No rider IDs, so frequency per person and conversion cannot be measured.
- **No prices, revenue or trip purpose** in the data; conversion rate and membership revenue are out of reach with this dataset.
- **Station data is incomplete:** about 30% of electric-bike rides have no start station.
- **One year of data;** seasonal patterns come from a single 12-month window.
- **Descriptive analysis only:** patterns show association, not cause.

## Author

Ali Akbar

## Reproducing this project

The data files are not stored in this repository (GitHub's 100 MB file limit). To reproduce:

1. Download the 12 monthly Divvy files (see [`02_Raw_Data/README.md`](02_Raw_Data/README.md)).
2. Run the cleaning and validation scripts (see [`03_Clean_Data/README.md`](03_Clean_Data/README.md)).
3. Run the SQL files in `05_SQL/` in PostgreSQL, then open `06_Python/cyclistic_analysis.ipynb`.

Scripts `00`-`17` contain absolute Windows paths in their configuration block; change them to your own before running.

## Repository history

This repository was assembled from a finished local project, so the commit history is organised by phase (Ask, Prepare, Process, Analyze, Share) rather than recording the original working sessions. Commit dates reflect when it was organised.
