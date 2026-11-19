\# Rajasthan Mandi Price \& Arrivals Intelligence



\# Detailed Analytical Report



\*\*Data source:\*\* AGMARKNET

\*\*Observation period:\*\* 1 January 2023 – 3 November 2026

\*\*Geographic scope:\*\* Rajasthan, India

\*\*Project type:\*\* Data analytics, reporting intelligence and source-level data quality investigation



\---



\## 1. Introduction



\### 1.1 Background



Agricultural market information is important for understanding commodity price movements and market activity. However, market datasets can contain irregular reporting patterns, incomplete time series and prolonged periods without recorded observations.



This project investigates these patterns using Rajasthan agricultural market data from AGMARKNET.



Rather than treating every missing record as an operational failure, the analysis examines reporting behaviour across weekdays, commodities, markets and time periods. It also compares raw source exports against processed analytical datasets to strengthen the reliability of its findings.



\### 1.2 Objectives



The project has the following objectives:



1\. Build a structured analytical dataset from raw AGMARKNET exports.

2\. Examine reporting patterns across weekdays and commodities.

3\. Analyse monthly reporting trends.

4\. Compare market–commodity reporting consistency against commodity-specific peer benchmarks.

5\. Identify and classify prolonged zero-reporting interruptions.

6\. Investigate trailing periods of reporting silence.

7\. Reconcile selected findings against raw source exports.

8\. Produce reproducible analytical outputs and stakeholder-ready visualisations.



\---



\## 2. Data Sources and Structure



\### 2.1 Source Data



The project uses 12 raw AGMARKNET CSV exports.



The source files contain agricultural market observations, including:



\- State and district.

\- Market/APMC name.

\- Commodity group.

\- Commodity name.

\- Observation date.

\- Arrival quantity.

\- Arrival unit.

\- Modal price.

\- Price unit.



The exports contain a metadata row before their column headers. The ingestion process accounts for this structure when reading the source files.



\### 2.2 Observation Coverage



| Dataset component | Records |

|---|---:|

| Raw source exports | 12 files |

| Calendar dimension | 1,461 dates |

| Market dimension | 186 markets |

| Commodity dimension | 18 commodities |

| Fact table | 439,399 observations |

| Eligible weekday/consistency pairs | 395 |

| Monthly pair-month panel | 17,093 rows |



The observed data period runs from 1 January 2023 through 3 November 2026, representing 1,403 calendar days.



The calendar dimension spans 1,461 dates. These two counts describe different things and should not be confused with verified market operating days.



\### 2.3 Analytical Measures



| Measure | Unit | Description |

|---|---|---|

| Arrival quantity | Metric Tonnes (MT) | Recorded commodity arrivals |

| Modal price | ₹/Quintal | Recorded modal market price |

| Reporting days | Days | Number of dates with recorded observations |

| Expected days | Calendar days | Calendar-span denominator |

| Reporting rate | Percentage | Reporting days divided by expected calendar days |



\### 2.4 Focus Commodities



The detailed weekday and peer-comparison analysis focuses on five commodities:



\- Bajra.

\- Barley.

\- Bengal Gram (Whole).

\- Mustard.

\- Wheat.



These five commodities account for 247,151 fact observations, approximately 56.25% of the total fact table.



\---



\## 3. Data Engineering and Dimensional Modelling



\### 3.1 Star Schema



The project transforms raw source records into a dimensional analytical model.



The model contains:



\- `dim\_date.csv`

\- `dim\_market.csv`

\- `dim\_commodity.csv`

\- `fact\_market\_arrivals.csv`



The fact table connects observations to date, market and commodity dimensions through their respective identifiers.



\### 3.2 Fact Table Grain



The intended grain is one observation per:



`(Date\_Id, Market\_Id, Commodity\_Id)`



The validation process confirms that this composite key is unique in the processed fact table.



\### 3.3 Data Quality Checks



The validation work includes:



\- Composite-key uniqueness.

\- Referential integrity against dimension tables.

\- Negative and zero price checks.

\- Negative arrival quantity checks.

\- Date parsing and invalid-row inspection.

\- Monthly panel completeness.

\- Reporting-rate bounds.

\- Duplicate pair-month detection.

\- Raw-versus-processed reconciliation.



\### 3.4 Date Parsing



Twenty-four unparseable date rows were identified. Inspection established that these rows were explanatory metadata, including `Note:` and weighted-average-price explanations, rather than genuine rejected market observations.



They were therefore treated as source-export metadata rather than valid market observations.



\### 3.5 Data Integrity Results



The processed data checks established:



\- No duplicate composite fact keys.

\- No orphan dimension keys.

\- No negative or zero modal prices.

\- No negative arrival quantities.

\- No duplicate market–commodity-month records in the monthly panel.

\- No missing values in the checked monthly panel.

\- Expected calendar days greater than zero.

\- Reported days not exceeding expected days.

\- Reporting rates within 0–100%.



These results describe the processed datasets and the checks performed; they are not a guarantee that every possible source-data issue has been eliminated.



\---



\## 4. Weekday Reporting Analysis



\### 4.1 Methodology



Weekday reporting analysis measures the proportion of calendar days with recorded observations for eligible market–commodity pairs.



The overall analysis uses 395 eligible pairs, each meeting the minimum threshold of 200 observed days.



The denominator is the calendar span used for each pair, not an independently verified trading calendar.



\### 4.2 Overall Weekday Results



| Weekday | Overall reporting rate |

|---|---:|

| Monday | 52.51% |

| Tuesday | 52.77% |

| Wednesday | 53.41% |

| Thursday | 51.78% |

| Friday | 50.83% |

| Saturday | 43.62% |

| Sunday | 5.40% |



\### 4.3 Interpretation



Wednesday has the highest overall calendar-span reporting rate, followed by Tuesday and Monday.



Saturday shows a lower rate than weekdays, while Sunday has a substantially lower rate.



This indicates a strong weekday pattern in the recorded data. However, it does not independently establish market operating hours, weekly closure schedules or the reason for missing observations.



!\[Overall weekday reporting rates](figures/01\_weekday\_reporting\_rates.png)



\### 4.4 Commodity-Level Weekday Results



The five focus commodities show different reporting levels.



| Commodity | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday | Sunday |

|---|---:|---:|---:|---:|---:|---:|---:|

| Bajra | 48.18% | 48.15% | 50.25% | 48.15% | 46.01% | 40.27% | 8.20% |

| Barley | 37.53% | 37.86% | 39.31% | 36.80% | 36.81% | 32.07% | 4.62% |

| Bengal Gram | 46.93% | 46.51% | 46.91% | 45.94% | 45.78% | 38.40% | 4.46% |

| Mustard | 59.06% | 60.20% | 60.40% | 58.74% | 57.97% | 49.93% | 5.13% |

| Wheat | 58.27% | 58.06% | 58.18% | 56.83% | 55.37% | 47.20% | 5.12% |



Mustard and Wheat have relatively higher reporting rates across weekdays. Barley has lower reporting rates in comparison.



The low Sunday rates occur across all five commodities.



!\[Commodity weekday reporting](figures/02\_commodity\_weekday\_reporting.png)



\---



\## 5. Monthly Reporting Trends



\### 5.1 Methodology



Monthly reporting analysis evaluates changes in recorded reporting activity over time.



The analysis uses monthly reporting rates by commodity and year, supported by a market–commodity-month panel.



Incomplete months are excluded from the complete-month trend comparison so that partial observation periods are not interpreted as full-month reporting performance.



The monthly panel contains 17,093 rows across 395 eligible market–commodity pairs.



\### 5.2 Interpretation



Monthly trends help identify periods of relatively high or low recorded reporting activity.



The results should be interpreted descriptively. A change in reporting rate does not automatically identify its cause.



Potential explanations such as agricultural seasonality, procurement practices, market operations, holidays or source-system changes require independent evidence before they can be established.



!\[Monthly commodity reporting trends](figures/03\_monthly\_commodity\_reporting\_trends.png)



\---



\## 6. Market–Commodity Reporting Consistency and Peer Benchmarking



\### 6.1 Objective



A simple reporting-rate ranking may not fairly compare market–commodity pairs when their weekday reporting patterns differ.



The peer-benchmark analysis addresses this by comparing each pair against other eligible pairs for the same commodity.



\### 6.2 Methodology



The analysis:



1\. Selects eligible market–commodity pairs.

2\. Calculates their calendar-span reporting rates.

3\. Constructs commodity-specific peer benchmarks.

4\. Uses leave-one-pair-out comparisons so the evaluated pair does not contribute to its own benchmark.

5\. Adjusts the comparison for differences in weekday composition.

6\. Identifies low-ranked pairs for additional investigation.



The weekday-adjusted benchmark index provides a relative comparison against the commodity's peer reporting pattern.



\### 6.3 Benchmark Population



| Commodity | Eligible pairs | Mean reporting rate |

|---|---:|---:|

| Bajra | 58 | 41.02% |

| Barley | 50 | 31.88% |

| Bengal Gram | 64 | 39.10% |

| Mustard | 120 | 50.19% |

| Wheat | 103 | 48.08% |

| \*\*Total\*\* | \*\*395\*\* | — |



\### 6.4 Selected Examples



| Commodity | Market | Actual reporting rate | Peer reporting rate | Adjusted index |

|---|---|---:|---:|---:|

| Mustard | Barisadri | 15.47% | 50.55% | 30.61 |

| Wheat | Nohar | 15.35% | 48.75% | 31.47 |

| Bajra | Osiyan Mathania | 14.59% | 41.82% | 34.90 |



These examples demonstrate substantial differences between selected pairs and their commodity-specific peers.



\### 6.5 Ranking Interpretation



Fifteen low-ranked market–commodity pairs were selected for deeper investigation.



The rankings are calculated within each commodity. They should not be interpreted as a global ranking of all market–commodity combinations.



The peer comparison is a screening tool for identifying unusual reporting patterns, not a measure of market performance or commercial quality.



!\[Selected low-ranked market commodity pairs](figures/04\_market\_reporting\_vs\_peer\_benchmark.png)



\---



\## 7. Zero-Reporting Interruption Analysis



\### 7.1 Objective



The interruption analysis investigates periods in which a market–commodity pair has no recorded observations.



A zero-reporting period for one commodity does not necessarily imply that the entire market had no recorded activity.



To investigate this distinction, the analysis examines other commodity records at the same market during the target commodity's interruption period.



\### 7.2 Classification Rules



The analysis uses three classifications.



\*\*Commodity-specific\*\*



Other commodities have recorded activity at the same market during the target commodity's interruption.



\*\*Potentially market-wide\*\*



No other commodity activity is recorded at the same market during the relevant target interruption period.



\*\*Mixed\*\*



Other commodity activity is recorded in some interruption months but not all.



These labels describe patterns in the source records. They do not prove physical market closure or a market-wide technical outage.



\### 7.3 Classification Results



| Classification | Number of events |

|---|---:|

| Commodity-specific | 65 |

| Potentially market-wide | 7 |

| Mixed | 4 |

| \*\*Total\*\* | \*\*76\*\* |



Of the 76 events, 75 had at least one month with peer activity during the target commodity's zero-reporting period.



The monthly activity audit contains 195 event-month records:



\- 63 months classified as market-inactive at the source-record level.

\- 132 months with activity recorded in other commodities.



!\[Interruption event classification](figures/05\_interruption\_event\_classification.png)



\### 7.4 Interpretation



The classification provides additional context for interpreting zero-reporting events.



Where other commodities continue to appear in source records, the interruption is more consistent with a commodity-specific reporting gap.



Where no other commodity activity is recorded, the evidence supports only a potentially market-wide source-level silence classification.



Further operational or administrative evidence would be required to determine the actual cause.



\---



\## 8. Source-Level Interruption Reconciliation



\### 8.1 Objective



The interruption reconciliation compares selected processed findings with the original downloaded source exports.



The purpose is to determine whether the observed source-level gaps are also present in the raw files.



\### 8.2 Reconciliation Results



The interruption audit summary contains four reviewed cases.



| Market | Finding | Period | Raw rows | Processed rows |

|---|---|---|---:|---:|

| Osiyan Mathania APMC | Source-level prolonged silence | 17 months | 0 | 0 |

| Barisadri APMC | Source-level prolonged silence | 15 months | 0 | 0 |

| HanumangarhTown APMC | Exact-label source-level silence | 6 months | 0 | 0 |

| Kotputli APMC | Intermittent source reporting | 8 months | 10 | 10 |



\### 8.3 Important Market-Name Handling



Market names are compared using trimmed, case-insensitive exact-label matching.



Internal spaces are preserved.



Consequently, labels such as:



\- `HanumangarhTown`

\- `Hanumangarh Town`

\- `Hanumangarh`



are not automatically treated as identical.



This avoids silently merging distinct source labels without supporting evidence.



\### 8.4 Kotputli Reconciliation



Kotputli had 10 raw records across four active dates during its audited interruption period.



Those records belonged to other commodities:



\- Bajra: 3 rows.

\- Mustard: 2 rows.

\- Potato: 2 rows.

\- Tomato: 3 rows.



No Wheat observations were recorded in those rows.



The raw and processed counts match, supporting the finding that the target Wheat pair had no recorded observations during the audited zero-reporting periods while other commodity records were present.



\### 8.5 Interpretation



The reconciliation strengthens confidence that the identified gaps are present in the downloaded source exports and were not introduced merely by the processing pipeline.



It does not establish why the source records are absent.



\---



\## 9. Trailing Reporting Silence Analysis



\### 9.1 Objective



Trailing reporting silence analysis identifies market–commodity pairs with an extended period since their latest recorded observation.



The dataset cutoff used for this analysis is \*\*3 November 2026\*\*.



\### 9.2 Selected Findings



| Market | Commodity | Last recorded date | Days since last observation |

|---|---|---|---:|

| Kotputli | Wheat | 27 June 2026 | 129 |

| Bhilwara | Mustard | — | 75 |

| Sardar Shahar | Mustard | — | 63 |

| Anupgarh | Bengal Gram | — | 50 |

| Raniwara | Mustard | — | 42 |

| Barisadri | Mustard | 16 October 2026 | 18 |

| Sumerpur | Mustard | 3 November 2026 | 0 |



The table reports the verified day counts. Where a date is not reproduced here, the day count should be taken from the detailed findings CSV rather than inferred.



\### 9.3 Kotputli–Wheat Case



Kotputli–Wheat is the longest selected trailing-silence case.



\- Last recorded Wheat observation: 27 June 2026.

\- Dataset cutoff: 3 November 2026.

\- Elapsed time: 129 days.

\- Trailing period: four full months and one partial month.

\- All five audited pair-months were classified as potentially market-wide at the source-record level.



This classification means that no other commodity activity was found at the same market in the audited months. It is not proof that Kotputli mandi was physically closed or non-operational.



\### 9.4 Raw-versus-Processed Reconciliation



The trailing-silence audit contains 22 pair-month records.



Raw-versus-processed activity counts and dates matched for all 22 records.



This is a zero-to-zero reconciliation check for the audited silence periods. It should not be interpreted as proof of every possible positive-record transformation.



\### 9.5 Selected Low-Reporting Pair Findings



The final selected-pair findings contain 15 pairs:



\- 13 reconciliation results marked PASS.

\- 2 marked NOT APPLICABLE.

\- 12 commodity-specific source-silence pair-months.

\- 5 potentially market-wide source-silence pair-months.



All five potentially market-wide pair-months belong to the Kotputli–Wheat case.



!\[Trailing reporting silence](figures/06\_trailing\_reporting\_silence.png)



\### 9.6 Interpretation



Trailing silence is useful for identifying pairs that deserve further review.



It should not be converted directly into a claim about mandi closure, commodity availability or farmer selling conditions.



Additional evidence such as market notices, official operating calendars or independent transaction records would be needed for those conclusions.



\---



\## 10. Analytical Limitations



The following limitations apply to the analysis.



\### 10.1 Calendar Days Versus Trading Days



The reporting denominator uses calendar days, not verified trading days.



Therefore, reporting rates measure source-record presence across a calendar span rather than the percentage of scheduled market sessions with reporting.



\### 10.2 Source Coverage



The analysis is limited to the downloaded AGMARKNET exports and their observation period.



Records outside the source files cannot be assumed to be absent from the live system.



\### 10.3 Missing Records



A missing observation is evidence of missing source-level reporting in the downloaded files.



It is not independent evidence of:



\- Physical market closure.

\- No trading activity.

\- Commodity unavailability.

\- A government or AGMARKNET outage.

\- A specific administrative decision.



\### 10.4 Causal Interpretation



The project identifies patterns and associations. It does not establish that weather, procurement policy, harvest timing, holidays or market operations caused the observed reporting changes.



\### 10.5 Market Labels



Exact-label reconciliation intentionally avoids automatically merging similar market names. A separate authoritative market master would be needed to resolve all potential aliases.



\### 10.6 Price Interpretation



The project includes modal prices and arrivals, but the reporting analyses do not establish that a particular market or date offers the best selling opportunity.



A farmer-facing recommendation would require additional analysis of price comparability, transport costs, market access, quality differences and current data availability.



\---



\## 11. Reproducibility and Project Execution



\### 11.1 Dependencies



Runtime and development dependencies are pinned in:



\- `requirements.txt`

\- `requirements-dev.txt`



Install the development dependencies using:



```powershell

python -m pip install -r requirements-dev.txt

```



\### 11.2 Run the Full Data Pipeline



```powershell

python .\\scripts\\run\_pipeline.py

```



The pipeline orchestrates the data preparation, analytical and audit stages, then runs the regression test suite.



\### 11.3 Run Tests Independently



```powershell

python -m pytest .\\tests -v

```



The current regression suite contains 27 tests covering dimensions, fact integrity, reporting panels and reconciliation.



These tests validate processed outputs. They do not independently re-read every raw export as a separate end-to-end ingestion test.



\### 11.4 Generate Analytical Charts



```powershell

python .\\scripts\\generate\_analytical\_charts.py

```



Chart generation is currently a separate step from the main pipeline.



\### 11.5 Raw Data Requirement



Raw AGMARKNET exports are excluded from the Git repository.



A clean checkout therefore requires the necessary source CSV exports to be supplied in `data/raw/` before the complete pipeline can be reproduced.



\---



\## 12. Project Outputs



\### 12.1 Core Processed Data



The `data/processed/` directory contains the dimensional model and analytical datasets, including:



\- Date, market and commodity dimensions.

\- Market-arrival fact table.

\- Weekday reporting summaries.

\- Commodity weekday reporting summaries.

\- Monthly reporting panels.

\- Market reporting consistency metrics.

\- Low-reporting peer comparisons.

\- Interruption event classifications.

\- Interruption raw-versus-processed audit outputs.

\- Trailing-silence findings and reconciliation outputs.



\### 12.2 Analytical Figures



The `reports/figures/` directory contains six generated charts:



1\. `01\_weekday\_reporting\_rates.png`

2\. `02\_commodity\_weekday\_reporting.png`

3\. `03\_monthly\_commodity\_reporting\_trends.png`

4\. `04\_market\_reporting\_vs\_peer\_benchmark.png`

5\. `05\_interruption\_event\_classification.png`

6\. `06\_trailing\_reporting\_silence.png`



\### 12.3 Supporting Audit Reports



\- `source\_level\_reporting\_interruption\_audit.md`

\- `trailing\_reporting\_silence\_audit.md`



These provide more detailed evidence for the interruption and trailing-silence investigations.



\---



\## 13. Conclusion



This project develops a structured analytical workflow for investigating agricultural market reporting patterns across Rajasthan.



The analysis demonstrates that reporting rates vary substantially by weekday, commodity and market–commodity pair. Peer benchmarking identifies selected pairs with unusually low reporting relative to their commodity peers. Interruption classification and raw-source reconciliation provide additional context for interpreting prolonged reporting gaps.



The strongest contribution is the combination of descriptive analytics with explicit source-level reconciliation. Rather than treating missing records as proof of market inactivity, the project distinguishes what the downloaded records demonstrate from what would require additional evidence.



The resulting datasets, audit outputs, charts, automated pipeline and regression tests provide a reproducible foundation for further agricultural market intelligence work.



\---



\## 14. Scope Disclaimer



This report is an analytical study of AGMARKNET source-level reporting patterns.



It is not an official assessment of Rajasthan mandi operations, a live market-price service, a commodity price forecast, or a recommendation to farmers or traders about where or when to sell.



All findings should be interpreted within the source coverage, observation period and methodological limitations described in this report.
