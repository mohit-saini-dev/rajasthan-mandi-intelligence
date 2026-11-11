# Rajasthan Agricultural Market Price & Arrivals Intelligence

A data engineering and analytical audit project using official AGMARKNET agricultural market data from Rajasthan, India.

## Project Overview

This project builds a reproducible analytical pipeline to examine agricultural market arrivals, modal prices, and reporting patterns across Rajasthan's Agricultural Produce Market Committee (APMC) markets.

The focus is not simply on price trends. It also investigates the consistency of market-level reporting, identifies prolonged reporting interruptions, compares reporting behaviour against commodity peers, and reconciles selected findings against the original downloaded source exports.

## Project Objectives

- Build a structured dataset from multiple AGMARKNET CSV exports.
- Clean and validate market, commodity, date, arrival and modal-price fields.
- Develop a dimensional star schema for analytical use.
- Measure weekday and monthly reporting patterns.
- Identify market–commodity pairs with unusually low reporting activity.
- Detect consecutive reporting interruptions and trailing reporting silence.
- Compare reporting activity against peer markets for the same commodity.
- Reconcile selected interruptions against the original source exports.

## Dataset Overview

The processed dataset contains:

| Metric | Value |
|---|---:|
| Fact observations | 439,399 |
| Markets | 186 |
| Commodities | 18 |
| Commodity groups | 6 |
| Source CSV exports | 12 |
| Observation period | 2023–2026 |
| Selected crops for deeper analysis | 5 |

The five selected commodities are:

- Bajra (Pearl Millet)
- Mustard
- Bengal Gram (Whole)
- Wheat
- Barley (Jau)

The dataset includes arrival quantities measured in Metric Tonnes and modal prices measured in Indian Rupees per Quintal.

The analysis cutoff for the reporting-silence investigation is 3 November 2026.

## Technology Stack

- Python 3.12
- Pandas
- NumPy
- CSV-based data storage
- Git and GitHub

## Data Engineering Pipeline

The project follows these main stages:

1. **Source ingestion:** Read downloaded AGMARKNET CSV exports and handle report metadata rows.
2. **Data preparation:** Standardize fields, parse dates, and prepare market and commodity identifiers.
3. **Dimensional modelling:** Build date, market and commodity dimensions alongside the market-arrivals fact table.
4. **Validation:** Check key integrity, fact-table grain, rejected dates and numerical ranges.
5. **Analytical transformations:** Generate temporal, weekday, monthly and market-level reporting datasets.
6. **Source reconciliation:** Compare selected processed-data interruptions against the original downloaded exports.

### Star Schema

The dimensional model consists of:

- `dim_date`
- `dim_market`
- `dim_commodity`
- `fact_market_arrivals`

The fact table uses date, market and commodity identifiers to connect observations to their dimensions.

## Analytical Investigations

### 1. Temporal Reporting Gaps

Examines reporting coverage and consecutive missing calendar-day intervals for market–commodity pairs.

### 2. Weekday Reporting Patterns

Compares reporting rates across the seven weekdays, including commodity-level differences.

### 3. Monthly Reporting Patterns

Builds a pair-month panel and compares observed reporting days with calendar-day exposure within each pair's observation period.

### 4. Peer-Adjusted Market Reporting Consistency

Compares each market's reporting rate against a leave-one-pair-out benchmark for the same commodity and weekday distribution.

### 5. Zero-Reporting Interruption Analysis

Identifies consecutive months with no reports and examines whether other commodity observations were present in the same market during those periods.

### 6. Source-Level Reconciliation

Checks selected market–commodity interruption periods against the original raw AGMARKNET exports to distinguish source-level absence from potential processing loss.

### 7. Trailing Reporting Silence

Examines the period between the last observed report and the dataset cutoff, distinguishing complete silent months from partial months.

## Selected Findings

- Sunday reporting was substantially lower than reporting on other weekdays in the selected five-crop analysis.
- Reporting rates varied across commodities and individual market–commodity pairs.
- Fifteen low-reporting pairs were selected for deeper interruption and trailing-silence diagnostics.
- Seven interruption events were classified as potentially market-wide in the earlier interruption-period investigation, representing six distinct market-periods.
- In the trailing-silence investigation, Kotputli Wheat was the only selected pair with potentially market-wide source silence at the dataset cutoff.
- The longest trailing silence in the selected pairs was Kotputli Wheat, last observed on 27 June 2026.

These are descriptive findings from the downloaded dataset, not proof of physical market closure or an AGMARKNET system outage.

## Repository Structure

```text
rajasthan-mandi-intelligence/
│
├── data/
│   ├── raw/                 # Local source exports; excluded from Git
│   └── processed/           # Processed datasets and analytical outputs
│
├── reports/                 # Markdown audit reports
│
├── scripts/                 # Python pipeline and analysis scripts
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

Python 3.12 or a compatible Python 3 version is recommended.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Data Availability

Raw AGMARKNET exports are not included in the Git repository.

To reproduce the pipeline from source, obtain the corresponding AGMARKNET exports and place them in:

```text
data/raw/
```

Processed datasets and selected analytical outputs are available under:

```text
data/processed/
```

Individual scripts are available under `scripts/`.

The pipeline currently consists of individual Python scripts rather than a single command-line orchestration entry point. Script execution order and input/output dependencies should be followed when reproducing the full workflow.

## Important Methodological Limitations

- Calendar-span reporting rates use calendar days between observed dates, not verified market operating or crop trading days.
- Missing observations do not automatically indicate reporting failures.
- Zero-reporting periods may reflect source-data absence, seasonal inactivity, market-specific conditions or other causes.
- Source-level silence means that records were absent from the downloaded exports; it does not establish physical market closure or an AGMARKNET outage.
- The downloaded exports cover the selected markets and commodities, not necessarily every Rajasthan market or agricultural commodity.
- November 2026 is a partial observation month because the dataset cutoff is 3 November 2026.

## Future Improvements

- Add automated pipeline orchestration.
- Add structured logging and configurable input/output paths.
- Improve geographic and commodity metadata enrichment.
- Add price and arrivals trend analysis, including weighted price metrics.
- Develop an interactive dashboard for market-level exploration.
- Add automated data-quality and regression tests.

## Author

**Mohit Saini**

GitHub: [mohit-saini-dev](https://github.com/mohit-saini-dev)

Project repository: [rajasthan-mandi-intelligence](https://github.com/mohit-saini-dev/rajasthan-mandi-intelligence)
