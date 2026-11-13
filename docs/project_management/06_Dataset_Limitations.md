# Dataset Limitations

## Known Limitations

### 1. Station-Level Missingness

**Issue:**

A substantial proportion of rides have missing start or end station information. Station missingness is particularly common among electric-bike trips.

**Potential impact:**

This limitation affects station-level analysis, including identifying the most popular starting stations, destinations, and station-to-station routes.

It does not prevent the core comparison of annual members and casual riders because rider type, ride ID, timestamps, and bike type are available.

**Planned handling:**

Retain these rides for the core analysis. Station-based analyses will use available station information and clearly disclose the missing-data limitation.

### 2. Duplicate Ride Records

**Issue:**

35 ride IDs appear in both the April 2026 and May 2026 files. Investigation showed that all 35 records are exact duplicates.

**Potential impact:**

Keeping both copies would double-count those rides and could inflate ride counts and other aggregated metrics.

**Planned handling:**

During PROCESS, retain one copy of each duplicated ride and remove the duplicate occurrence using a documented, reproducible rule.

### 3. Negative Ride Durations

**Issue:**

29 records have negative calculated ride durations. All were observed around the daylight-saving-time transition on November 2, 2025.

**Potential impact:**

These records would distort duration statistics if treated as normal ride durations.

**Planned handling:**

Do not delete the original records automatically. Flag the affected records and apply an explicit, documented treatment during PROCESS so the original data remains traceable.

### 4. Missing End Coordinates

**Issue:**

5,426 rides (0.0887%) in the raw files have missing `end_lat` and `end_lng` values. After the 35 duplicates are removed, 5,420 remain.

**Potential impact:**

This affects geographic analysis of ending locations and any analysis requiring both start and end coordinates.

The impact on overall ride counts and the core member-versus-casual comparison is minimal.

**Planned handling:**

Retain the records. Exclude them only from analyses that specifically require complete ending coordinates.

### 5. Missing Contextual Variables

**Issue:**

The dataset does not include variables such as weather, rider demographics, income, trip purpose, or bike availability.

**Potential impact:**

The available data can reveal descriptive usage patterns, but it cannot by itself establish why those patterns occur or prove that one factor caused another.

**Planned handling:**

Limit conclusions to patterns supported by the available data. Avoid causal claims unless additional data is introduced and analyzed.

### 6. No Rider IDs, Prices or Revenue

**Issue:**

The trip files record rides, not riders. They have no rider ID, no ticket or membership price and no revenue field.

**Potential impact:**

The number of rides per person, repeat use and the time from a first casual ride to a membership cannot be measured. Membership revenue, price break-even and conversion rate cannot be calculated. Counts are of rides, not of riders.

**Planned handling:**

State clearly that findings describe rides, not people. Recommend testing any offer with Cyclistic's own rider-level data, for example a split test against a control group.

## Overall Data Limitations

The dataset is suitable for descriptive analysis of differences between annual members and casual riders, but some analyses have important limitations.

Station and route analyses are affected by missing station information, while duration analysis requires special treatment of the 29 negative-duration records. The absence of contextual variables also limits causal interpretation.

These limitations will be explicitly documented in the final analysis and visualizations.

## Final PREPARE Conclusion

### Is the dataset ready for PROCESS?

**Yes.**

The dataset is sufficiently complete and structurally consistent to proceed to PROCESS and answer the assigned business question about differences in usage between annual members and casual riders.

However, PROCESS must:

1. Remove the 35 confirmed duplicate ride records.
2. Apply a documented treatment to the 29 DST-related negative-duration records.
3. Preserve rides with missing station or coordinate information unless a specific analysis requires those fields.
4. Clearly distinguish descriptive findings from causal explanations.
5. Document all cleaning and transformation decisions so the analysis is reproducible.