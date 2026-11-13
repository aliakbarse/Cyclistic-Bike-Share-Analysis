# Cyclistic Bike-Share: How Members and Casual Riders Differ

**Prepared for:** Director of Marketing, Marketing Analytics Team, Executive Team
**Author:** Ali Akbar
**Data:** 6,115,947 rides, September 2025 - August 2026
**Status:** Analysis complete. Interactive dashboard (Power BI) is the next deliverable.

---

## 1. Executive summary

Cyclistic wants more annual members. This analysis compares how members and casual riders use the service, to find where casual riders look most like members and when they are most reachable.

**The short answer:** casual riders are a seasonal, weekend-leaning group; members ride all year, mostly on weekdays with morning and late-afternoon peaks. The two groups are not opposites, though. More than a quarter of casual rides already look like member rides, and in this year of data casual riding rose sharply from April to May.

| | Member | Casual |
|---|---|---|
| Share of rides | 64.7% | 35.3% |
| Median ride | 8.6 min | 10.9 min |
| Weekend share of rides | 23% | 37% |
| Summer (Jun-Aug) share of rides | 38% | 47% |
| Commute-like weekday rides* | 44% | 28% |
| Rides starting 06:00-09:59 | 20% | 11% |

*Weekday, starting 06-09 or 16-19, under 30 minutes.

**Three things to act on**

1. **Target casual riders who already ride like members.** About 602,000 casual rides (28% of casual rides) are weekday, commute-window, short rides. This is the closest behavioural match to members in the data.
2. **Time campaigns to the spring ramp-up seen in this year's data.** Casual rides nearly double from April (131,500) to May (245,100), and casual share of all rides climbs from 29% to 37%. Casual riding peaks in July at 358,000 rides, against 25,000 in January.
3. **Use rider-level data Cyclistic already has to size the opportunity.** This public trip data has no rider IDs or prices, so it shows *who rides when* but cannot show *who would switch*. A pricing break-even and a test campaign are the next step.

---

## 2. Business task and questions

**Task:** analyse the differences between casual riders and annual members to identify opportunities to convert casual riders into members.

1. How do annual members and casual riders use Cyclistic bikes differently?
2. Why would casual riders buy annual memberships?
3. How can Cyclistic use digital media to influence casual riders to become members?

## 3. Data and method

- **Source:** 12 monthly Divvy trip files, 6,115,982 raw records, 13 columns.
- **Cleaning:** 35 exact cross-file duplicate rides removed; 29 negative durations at the 2 Nov 2025 daylight-saving change flagged and corrected by +60 minutes; rides with missing station or end-coordinate data kept (excluded only from station-specific analysis). Result: 6,115,947 rides. Full rules in `docs/project_management/07_Process_Cleaning_Plan.md`.
- **Tools:** Python (cleaning, validation, notebook), PostgreSQL-syntax SQL (analysis), Excel (summary tables), Power BI (dashboard, next).
- **Verification:** the same headline metrics were computed independently in SQL and in pandas and agree exactly (checked in `notebooks/cyclistic_analysis.ipynb`, section 2).
- **Month definition:** the dataset's file month (`LEFT(source_file, 6)`), so rides that cross a month boundary stay with their source file.

## 4. Findings

### Q1. How do members and casual riders use bikes differently?

**Timing**

- Both groups peak at 17:00 on weekdays. The difference is the morning: 20% of member rides start between 06:00 and 09:59, versus 11% of casual rides.
- On weekends the hourly profiles are almost identical. Casual riders differ in *how much* they ride on weekends (37% of their rides), not *when*.
- Charts: `docs/images/01_hourly_profile.png`, `02_weekday_hour_heatmap.png`

**Seasonality**

- 47% of casual rides fall in June-August, against 38% of member rides. In winter, casual riders are only 4% of casual annual volume (members: 10%).
- Casual share of all rides runs from 18% (January) to 41% (July).
- Chart: `03_monthly_rides_and_casual_share.png`

**Ride length**

- Median ride: casual 10.9 min, member 8.6 min (1.27x).
- The mean gap is larger (20.7 vs 12.4 min, 1.67x) because a few very long rides inflate casual averages. After removing rides under 1 minute and over 3 hours the gap is 1.46x. The direction holds under every treatment, but the size depends on how outliers are handled, so medians are the safer figure to quote.
- Casual classic-bike rides are the main source of long rides: mean 37-43 min, median 14-18 min.
- Chart: `04_duration_distribution.png`

**Bike type**

- Electric-bike use is similar (74% casual, 68% member). Bike type does not separate the groups.

**Places**

- Casual riders are the majority at lakefront and tourist stations, e.g. Shedd Aquarium (82% casual), Field Museum (81%), Navy Pier (76%, the busiest casual start station with about 51,700 casual rides).
- Casual riders make round trips (same start and end station) more often: 10% of classic-bike rides versus 2% for members.
- Casual riding is **dispersed**: the ten busiest casual stations hold about 10% of casual rides.
- Chart: `05_top_casual_stations.png`

### Q2. Why would casual riders buy annual memberships?

The data cannot answer *why*. There is no price, trip-purpose, or rider-level information. It does show which riders have the strongest behavioural overlap with members, which is where a membership offer is most plausible:

- **Commute-like casual riders (about 602,000 rides, 28% of casual rides).** They ride on weekday commute schedules like members. Hypothesis to test: a per-ride price comparison is most favourable for frequent, regular riders.
- **Short weekend riders on electric bikes (about 504,000 casual rides under 30 minutes).** Their median ride (9.6 min) is close to members' (8.4 min). They are over-represented relative to members in weekend short-ride segments by 3 to 5 percentage points. Hypothesis: a lower-commitment or seasonal offer fits them better than a full annual plan.
- **Long-ride and tourist-pattern casual riders** (long durations, round trips, lakefront and museum stations). They show the weakest overlap with members and are the least likely conversion candidates from this evidence.

These are behavioural segments at the ride level. They are not people, and nothing here estimates a conversion rate.

### Q3. How can Cyclistic use digital media to influence casual riders?

Recommendations follow from the timing and location patterns above:

1. **Run the campaign window April-June.** Casual volume is ramping up (April to May: +86% casual rides versus +29% for members), so the pool of reachable casual riders is growing fastest then.
2. **Use in-app and email messages at the moments casual riders ride:** weekday afternoons (peak 17:00) and weekends, with a savings message for weekday riders.
3. **Treat stations as a supporting channel, not the main one.** Geo-targeted promotion at the top lakefront stations makes sense (they are majority-casual), but even the top 15 stations hold only about 12% of casual rides. In-app and email reach far more.
4. **Test, don't assume.** Run a split test of a membership offer on casual riders in the commute-like segment against a control group, using Cyclistic's own rider-level data.

## 5. Recommendations

| # | Recommendation | Evidence | Confidence |
|---|---|---|---|
| 1 | Prioritise commute-like casual riders for membership messaging | 28% of casual rides match the member weekday pattern | Medium: ride-level, no purpose data |
| 2 | Launch campaigns in April-June as casual volume ramps | Casual rides +86% April to May; casual share 29% to 37% | High for the pattern, one year of data |
| 3 | Offer a seasonal or lower-commitment option to weekend/summer riders | 47% of casual rides in summer; winter nearly absent | Medium: needs price testing |
| 4 | Use in-app/email as primary channel, stations as secondary | Top 15 stations hold about 12% of casual rides | High |
| 5 | Pull rider-level data to measure frequency and price break-even | Not possible with public trip data | n/a |

## 6. Limitations

- **Rides are not riders.** No rider IDs, so no frequency per person and no conversion measurement.
- **No prices, revenue or trip purpose.** The brief lists membership revenue and conversion rate as metrics; neither can be computed from this dataset.
- **Station data is incomplete.** About 30% of electric-bike rides have no start station, so station and round-trip findings describe the rides that do.
- **One year of data.** Seasonal patterns come from a single 12-month window.
- **Descriptive only.** Patterns show association, not cause. "Commute-like" describes timing and length, not purpose.

## 7. Next step

Build the Power BI dashboard from the SQL result tables (`sql/04_final_queries.sql` and `sql/03_analysis.sql`) so stakeholders can explore the timing, season and station patterns interactively.

## Appendix: where things are

| What | Where |
|---|---|
| Cleaning and validation scripts | `src/cyclistic/clean.py`, `src/cyclistic/validate.py`, `tests/` |
| Analysis and verification notebook | `notebooks/cyclistic_analysis.ipynb` |
| SQL | `sql/01-04_*.sql` |
| Summary tables | `excel/summary_tables.xlsx` |
| Charts | `docs/images/` |
