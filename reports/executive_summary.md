\# Rajasthan Mandi Price \& Arrivals Intelligence



\## Executive Summary



\### Project Overview



Rajasthan Mandi Price \& Arrivals Intelligence is a data analytics project examining agricultural commodity reporting patterns across Rajasthan's agricultural markets.



The project uses AGMARKNET market-arrival and modal-price records to investigate reporting consistency, weekday patterns, commodity-level differences, prolonged reporting interruptions, and trailing periods of source-level reporting silence.



The objective is to turn large, fragmented market-reporting datasets into structured, reproducible analysis that can help identify reporting patterns and areas requiring further investigation.



\*\*Important:\*\* This project analyses the availability of records in downloaded source data. It does not establish whether a physical mandi was open or closed, whether trading actually occurred, or whether AGMARKNET experienced a technical outage.



\---



\## 1. Dataset at a Glance



| Metric | Value |

|---|---:|

| Source | AGMARKNET |

| Raw source exports | 12 CSV files |

| Observation period | 1 January 2023 – 3 November 2026 |

| Calendar dimension | 1,461 dates |

| Markets | 186 |

| Commodities | 18 |

| Fact records | 439,399 |

| Eligible market–commodity pairs for weekday and consistency analysis | 395 |

| Monthly market–commodity panel | 17,093 rows |

| Focus commodities | 5 |



\### Main analytical measures



\- \*\*Arrival quantity:\*\* Metric Tonnes (MT).

\- \*\*Modal price:\*\* Indian Rupees per Quintal (₹/Quintal).

\- \*\*Reporting rate:\*\* Observed reporting days divided by calendar days in the applicable analysis period.



The five focus commodities are Bajra, Barley, Bengal Gram, Mustard and Wheat.



\---



\## 2. Principal Findings



\### 2.1 Weekday Reporting Patterns



Reporting rates vary substantially across weekdays.



\- Wednesday has the highest overall calendar-span reporting rate at approximately \*\*53.41%\*\*.

\- Tuesday follows at approximately \*\*52.77%\*\*.

\- Saturday falls to approximately \*\*43.62%\*\*.

\- Sunday has a substantially lower rate of approximately \*\*5.40%\*\*.



These differences show that reporting is not evenly distributed across the calendar week. They should not, by themselves, be interpreted as proof of mandi operating schedules or closures.



!\[Overall weekday reporting rates](figures/01\_weekday\_reporting\_rates.png)



\### 2.2 Commodity-Level Weekday Differences



The weekday analysis also reveals differences between commodities.



Mustard and Wheat have relatively high weekday reporting rates in this dataset, while Barley and Bengal Gram generally have lower rates. Sunday reporting is notably low across all five focus commodities.



!\[Commodity weekday reporting](figures/02\_commodity\_weekday\_reporting.png)



\### 2.3 Monthly Reporting Trends



Monthly reporting patterns vary by commodity and year. The analysis uses complete months for the comparative trend chart to avoid treating partial months as directly comparable with full months.



The results are descriptive. They identify changes in recorded reporting activity but do not establish the agricultural, weather, procurement or operational causes behind those changes.



!\[Monthly commodity reporting trends](figures/03\_monthly\_commodity\_reporting\_trends.png)



\### 2.4 Market–Commodity Reporting Consistency



A peer-benchmark analysis evaluates reporting consistency among eligible market–commodity pairs.



\- \*\*395 eligible pairs\*\* were assessed.

\- Each pair was compared against a commodity-specific peer benchmark.

\- The benchmark uses leave-one-pair-out comparisons.

\- The adjusted index accounts for differences in the pair's weekday composition.

\- Fifteen selected low-ranked pairs were examined in greater detail.



The ranking is performed within each commodity, rather than as a single global ranking across all market–commodity pairs.



!\[Selected low-ranked market commodity pairs](figures/04\_market\_reporting\_vs\_peer\_benchmark.png)



\### 2.5 Reporting Interruption Classification



The interruption analysis identified \*\*76 reporting interruption events\*\*:



| Classification | Events |

|---|---:|

| Commodity-specific | 65 |

| Potentially market-wide | 7 |

| Mixed | 4 |

| \*\*Total\*\* | \*\*76\*\* |



A total of 75 events had at least one month with activity in other commodities at the same market during the target commodity's zero-reporting period.



These classifications help distinguish commodity-specific reporting gaps from broader market-level source activity patterns. They are not proof of physical market closure or system outages.



!\[Interruption event classification](figures/05\_interruption\_event\_classification.png)



\### 2.6 Trailing Reporting Silence



The trailing-silence analysis evaluates market–commodity pairs with no recent recorded observations relative to the dataset cutoff of \*\*3 November 2026\*\*.



Notable examples include:



\- Kotputli – Wheat: last recorded observation on 27 June 2026.

\- Bhilwara – Mustard: 75 days since the last recorded observation.

\- Sardar Shahar – Mustard: 63 days.

\- Anupgarh – Bengal Gram: 50 days.

\- Raniwara – Mustard: 42 days.



The Kotputli–Wheat case received additional investigation. During its five audited trailing-silence pair-months, the source-level activity classification was potentially market-wide. This means the downloaded source records did not show activity for other commodities at that market in those audited months; it does not establish that the physical market was closed.



The raw-versus-processed reconciliation matched the audited zero-activity counts and dates across all 22 trailing-silence pair-month records.



!\[Trailing reporting silence](figures/06\_trailing\_reporting\_silence.png)



\---



\## 3. Data Quality and Reconciliation



The project includes structured validation and reconciliation checks.



Key results:



\- The fact table contains \*\*439,399 records\*\*.

\- The composite fact grain `(Date\_Id, Market\_Id, Commodity\_Id)` is unique.

\- No orphan dimension keys were identified.

\- No negative or zero modal prices were identified.

\- No negative arrival quantities were identified.

\- Twenty-four unparseable date rows were identified as explanatory metadata rows in source exports, rather than genuine rejected market observations.

\- The monthly reporting panel contains 17,093 rows across 395 eligible pairs.

\- Monthly panel checks found no duplicate pair-month records or missing values.

\- Reporting rates remain within the expected 0–100% range.

\- Exact-label raw-versus-processed reconciliation preserves distinctions between similar market names instead of automatically merging them.



The project also includes dedicated audits for interruption periods and trailing reporting silence.



\---



\## 4. Methodology and Limitations



The analysis is based on records present in the downloaded AGMARKNET exports.



Important methodological considerations:



1\. \*\*Calendar-span denominator:\*\* Reporting rates use calendar days within the applicable observation period. They are not verified trading-day or scheduled-operating-day rates.

2\. \*\*Source-level interpretation:\*\* An absent record indicates that no matching observation was found in the downloaded source data. It does not prove physical closure, non-operation, or a reporting-system outage.

3\. \*\*Peer comparisons:\*\* Benchmarks are commodity-specific and use leave-one-pair-out comparisons to reduce self-influence.

4\. \*\*Incomplete months:\*\* Partial months are excluded from the complete-month trend comparison.

5\. \*\*Descriptive findings:\*\* Observed patterns should not be treated as causal explanations without additional evidence.

6\. \*\*Market-name handling:\*\* Similar-looking market labels are retained separately unless exact reconciliation rules establish a match.

7\. \*\*Data cutoff:\*\* Trailing-silence findings are relative to the source dataset cutoff of 3 November 2026.



The findings are intended for analytical screening and further investigation, not as direct recommendations about when or where farmers should sell their produce.



\---



\## 5. Reproducibility



The project includes a Python pipeline, pinned dependencies, and automated regression tests.



\### Install dependencies



```powershell

python -m pip install -r requirements-dev.txt

```



\### Run the analytical pipeline



```powershell

python .\\scripts\\run\_pipeline.py

```



\### Run the regression tests independently



```powershell

python -m pytest .\\tests -v

```



\### Regenerate analytical charts



```powershell

python .\\scripts\\generate\_analytical\_charts.py

```



The pipeline orchestrates the data preparation and analytical stages. Chart generation is currently a separate command.



Raw AGMARKNET exports are excluded from the Git repository. Reproducing the complete analysis requires placing the required source CSV files in `data/raw/`.



\---



\## 6. Detailed Audit Reports



The following reports provide additional methodological and reconciliation detail:



\- \[Source-Level Reporting Interruption Audit](source\_level\_reporting\_interruption\_audit.md)

\- \[Trailing Reporting Silence Audit](trailing\_reporting\_silence\_audit.md)



\---



\## 7. Project Scope



This project demonstrates a reproducible analytical workflow covering:



\- Raw data inspection and transformation.

\- Dimensional modelling and fact-table construction.

\- Data quality validation.

\- Temporal and weekday reporting analysis.

\- Commodity-specific peer benchmarking.

\- Interruption classification.

\- Raw-versus-processed reconciliation.

\- Trailing reporting-silence investigation.

\- Automated pipeline execution and regression testing.

\- Stakeholder-oriented analytical visualisation.



\*\*Overall conclusion:\*\* The analysis demonstrates substantial variation in source-level reporting across weekdays, commodities and market–commodity pairs. Combining calendar-based reporting metrics, peer benchmarks and raw-source reconciliation provides a more defensible way to identify reporting irregularities than relying on isolated missing records.
