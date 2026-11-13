# ROCCC Assessment

## Business Question

How do annual members and casual riders use Cyclistic bikes differently?

## R — Reliable

**Assessment: Mostly reliable for the assigned business question**

The dataset contains more than 6.1 million ride records covering 12 months. Multiple data-quality checks were performed before analysis, including schema validation, missing-value analysis, duplicate investigation, duration validation, categorical integrity, and coordinate validation.

Several data-quality issues were identified, including 35 duplicated ride IDs, 29 negative ride durations associated with the daylight-saving time transition, and substantial missingness in station-related fields. These issues do not automatically make the dataset unreliable. Their impact must be assessed in relation to the business question.

Based on the investigations completed so far, the dataset remains suitable for comparing the usage behavior of annual members and casual riders, provided that identified limitations are documented and appropriate cleaning is performed during PROCESS.

## O — Original

**Assessment: Original source attribution is available**

The case-study material states that the Cyclistic datasets are public data made available by Motivate International Inc. under a license. Cyclistic itself is a fictional company created for the case study.

The Google Data Analytics certificate provides the case-study framework, but the dataset should not be described as data created by Google.

## C — Comprehensive

**Assessment: Sufficient for the assigned business question, but not comprehensive for causal analysis**

The dataset contains variables such as rider type, bike type, start and end times, stations, and geographic coordinates. These variables provide sufficient information to analyze how annual members and casual riders use the bike-share service differently.

However, the dataset does not contain potentially relevant variables such as rider demographics, weather conditions, bike availability, income, trip purpose, or membership purchase behavior.

These missing variables limit our ability to explain why behavioral differences occur or establish causal relationships. They do not prevent the analysis of observable usage patterns.

## C — Current

**Assessment: Appropriate for the case-study analysis**

The dataset covers the previous 12 months, from September 2025 through August 2026.

A full 12-month period provides coverage across all seasons and is appropriate for identifying annual usage patterns and differences between members and casual riders.

A longer historical period could provide additional year-over-year context, but the available 12-month period is sufficient for the assigned analysis.

## C — Cited

**Assessment: Source and licensing information can be documented**

The case-study material identifies the historical trip data as public data made available by Motivate International Inc. under a license.

The analysis should clearly cite the original data source and document the applicable licensing and privacy restrictions in the final portfolio project.

The dataset does not provide personally identifiable information, and the case-study material states that privacy restrictions prevent linking pass purchases to credit-card information.

## Overall Assessment

The dataset is suitable for the assigned business question because it contains sufficient information to compare observable usage patterns between annual members and casual riders.

However, the analysis must account for data-quality issues, missing station information, privacy restrictions, and the absence of variables needed to explain causal drivers such as weather, rider demographics, and bike availability.