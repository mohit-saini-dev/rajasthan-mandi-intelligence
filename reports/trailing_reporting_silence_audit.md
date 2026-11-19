# Trailing Reporting Silence Audit
## Rajasthan Agricultural Market Price & Arrivals Intelligence Pipeline

**Analysis cutoff:** 3 November 2026  
**Scope:** 15 low-reporting market–commodity pairs across five selected commodities  
**Source:** Downloaded AGMARKNET raw CSV exports and the project's processed fact and dimension tables

---

## 1. Objective

This audit investigates whether recent reporting gaps in selected Rajasthan market–commodity pairs are:

- Limited to the target commodity while other commodities continue reporting at the same market.
- Accompanied by an absence of records across all commodities for the exact market label in the downloaded source exports.
- Introduced during data processing or already present in the downloaded raw exports.

The analysis is designed to distinguish source-level reporting absence from processing-related record loss. It does not establish why a market or commodity is absent from the downloaded data.

## 2. Scope and selection

The analysis uses the 15 lowest-ranked market–commodity pairs from the peer-adjusted reporting consistency analysis.

The selected commodities are:

- Bajra (Pearl Millet/Cumbu)
- Barley (Jau)
- Bengal Gram (Gram) (Whole)
- Mustard
- Wheat

The trailing-silence diagnostic uses the dataset cutoff of **3 November 2026**.

The 15 pairs were not selected randomly. They were selected because of relatively low reporting indices compared with their respective commodity peers. Findings should therefore not be generalized to all Rajasthan markets.

## 3. Methodology

### 3.1 Trailing silence

For each selected pair, the analysis identifies its last observed reporting date and calculates the number of calendar days between that date and the dataset cutoff.

Complete silent calendar months and the current partial month are counted separately.

This distinction avoids treating an incomplete November 2026 as a complete month.

### 3.2 Raw-to-processed reconciliation

For each pair-month included in the trailing-silence diagnostic:

1. The exact market and commodity labels are matched against the downloaded raw exports.
2. Raw records are restricted to the relevant calendar month and dataset cutoff.
3. The corresponding processed market–commodity records are checked.
4. Raw and processed active-date counts are compared.

The audit covers 22 trailing pair-months.

All 22 pair-months have zero raw active dates and zero processed active dates. The observed absences were therefore already present in the downloaded raw exports.

This is a zero-to-zero reconciliation. It establishes that these audited absences were not introduced by processing, but it is not a positive row-by-row transformation test.

### 3.3 Activity across other commodities

All available commodity labels in the downloaded raw exports are examined for the same exact market label during each target pair-month.

Each pair-month is classified as:

- **Commodity-specific source silence:** at least one raw record exists for another commodity at the same market.
- **Potentially market-wide source silence:** no raw records exist for any commodity at that exact market label during the audited period.

These classifications describe the downloaded exports. They do not establish physical market closure or operational status.

### 3.4 Exact market labels

Market labels are normalized only for leading/trailing whitespace and case-insensitive matching. Internal spaces are preserved.

Distinct labels such as `HanumangarhTown APMC` and `Hanumangarh Town APMC` are not merged without independent evidence that they represent the same reporting entity.

## 4. Pair-level findings

| Market | Commodity | Last reported | Silent days | Full silent months | Partial silent months | Audited months | Classification |
|---|---|---:|---:|---:|---:|---:|---|
| Barisadri APMC | Mustard | 2026-10-16 | 18 | 0 | 1 | 1 | Commodity-specific |
| Sardar Shahar APMC | Mustard | 2026-09-01 | 63 | 1 | 1 | 2 | Commodity-specific |
| Nohar APMC | Wheat | 2026-10-19 | 15 | 0 | 1 | 1 | Commodity-specific |
| Sumerpur APMC | Mustard | 2026-11-03 | 0 | 0 | 0 | 0 | No trailing silence |
| Kotputli APMC | Wheat | 2026-06-27 | 129 | 4 | 1 | 5 | Potentially market-wide |
| HanumangarhTown APMC | Mustard | 2026-10-27 | 7 | 0 | 1 | 1 | Commodity-specific |
| Beawar APMC | Wheat | 2026-10-28 | 6 | 0 | 1 | 1 | Commodity-specific |
| Rawla APMC | Wheat | 2026-10-23 | 11 | 0 | 1 | 1 | Commodity-specific |
| Osiyan Mathania APMC | Bajra | 2026-10-26 | 8 | 0 | 1 | 1 | Commodity-specific |
| Raniwara APMC | Mustard | 2026-09-22 | 42 | 1 | 1 | 2 | Commodity-specific |
| HanumangarhTown APMC | Wheat | 2026-10-08 | 26 | 0 | 1 | 1 | Commodity-specific |
| Anupgarh APMC | Bengal Gram | 2026-09-14 | 50 | 1 | 1 | 2 | Commodity-specific |
| Sumerpur APMC | Bengal Gram | 2026-10-27 | 7 | 0 | 1 | 1 | Commodity-specific |
| Bhadara APMC | Wheat | 2026-11-02 | 1 | 0 | 0 | 0 | No trailing silence |
| Bhilwara APMC | Mustard | 2026-08-20 | 75 | 2 | 1 | 3 | Commodity-specific |

### Classification summary

| Finding | Pairs |
|---|---:|
| No trailing silence observed at dataset cutoff | 2 |
| Commodity-specific source silence only | 12 |
| Potentially market-wide source silence detected | 1 |
| **Total selected pairs** | **15** |

The 13 pairs with trailing months account for 22 audited pair-months.

## 5. Main finding: Kotputli APMC – Wheat

Kotputli Wheat is the only selected pair with potentially market-wide source silence in this trailing-period audit.

| Month | Raw records across all commodities | Active dates |
|---|---:|---:|
| July 2026 | 0 | 0 |
| August 2026 | 0 | 0 |
| September 2026 | 0 | 0 |
| October 2026 | 0 | 0 |
| November 1–3, 2026 | 0 | 0 |
| **Total** | **0** | **0** |

Key observations:

- Last observed Wheat report: 27 June 2026.
- Trailing silence at cutoff: 129 calendar days.
- Four complete silent calendar months followed by one partial month.
- No records for any commodity were found under the exact `Kotputli APMC` label in these five audited months.
- Raw and processed active-date counts matched in all five months.

This is evidence of market-wide source-export silence for the exact market label during the audited period. It is not evidence that the physical market was closed, that trading stopped, or that AGMARKNET experienced an outage.

## 6. Commodity-specific source silence

The other 12 pairs with trailing months had at least one record for another commodity at the same exact market label during each audited month.

Examples include:

- **Bhilwara APMC:** other commodities continued appearing while Mustard had no records in September, October and November 1–3, 2026.
- **Sardar Shahar APMC:** Groundnut records were present during the audited October and November periods while Mustard was absent.
- **Anupgarh APMC:** other commodities continued appearing while Bengal Gram was absent in October and November 1–3, 2026.
- **Raniwara APMC:** other commodities continued appearing during the audited October and November periods while Mustard was absent.

These observations indicate that the absence was commodity-specific within the downloaded exports, rather than a complete absence of records for the exact market label.

They do not prove that the target commodity was traded or should have been reported on those dates.

## 7. Raw-to-processed integrity results

| Check | Result |
|---|---:|
| Selected market–commodity pairs | 15 |
| Pairs with trailing months to audit | 13 |
| Pairs with no trailing months | 2 |
| Trailing pair-months audited | 22 |
| Pair-months with matching raw/processed active-date counts | 22 |
| Applicable pair-level reconciliation statuses | 13 PASS |
| Not applicable | 2 |
| Review failures | 0 |

The two not-applicable pairs are:

- Sumerpur APMC – Mustard: last report on 3 November 2026, the dataset cutoff.
- Bhadara APMC – Wheat: last report on 2 November 2026, with no complete or partial trailing month in the diagnostic.

The reconciliation checks passed for all applicable pairs.

Because all audited target pair-months contain zero raw and processed active dates, this test supports the conclusion that the observed absences were present in the source exports. It does not independently validate every transformation applied to positive observations elsewhere in the pipeline.

## 8. Limitations and interpretation

1. **Source coverage:** The audit examines the downloaded raw CSV exports, not the complete live AGMARKNET database.
2. **Market operation:** Missing records do not prove physical market closure, non-operation, or suspension of trading.
3. **Commodity activity:** Other commodities reporting at a market does not prove that the target commodity was available or traded.
4. **Exact labels:** Market labels are preserved as distinct identities. Similar-looking labels are not automatically merged.
5. **Overlapping exports:** Raw row counts may contain duplicate observations if downloaded exports overlap. Active dates and distinct commodity labels are more useful for interpreting market activity.
6. **Zero-to-zero reconciliation:** Matching zero raw and processed records verifies source-level absence for the audited periods, not positive record-level transformation accuracy.
7. **Selection bias:** The 15 pairs were selected because they ranked among the lowest peer-adjusted reporting indices. The results are not a representative sample of all markets.
8. **Partial month:** November 2026 is observed only through 3 November and should not be compared directly with a complete month.
9. **Reporting denominator:** Peer-adjusted reporting measures are based on the project's calendar-span reporting methodology, not verified market operating days or official crop trading calendars.

## 9. Conclusion

The trailing-silence investigation provides evidence that the selected reporting gaps were already present in the downloaded source exports rather than being introduced by the processing pipeline.

Among the 15 selected market–commodity pairs:

- 12 show commodity-specific source silence during their audited trailing months.
- One pair, Kotputli Wheat, shows potentially market-wide source silence across five consecutive audited months.
- Two pairs have no trailing-silence months at the dataset cutoff.

The most important follow-up candidate is Kotputli APMC, where no records for any commodity were found under the exact market label from July through November 3, 2026.

The appropriate conclusion is **source-level reporting absence**, not confirmed market closure, trading suspension, or AGMARKNET system failure.

---

## 10. Reproducibility: generated project outputs

The audit uses the following processed outputs:

- `trailing_silence_summary.csv`
- `trailing_silence_monthly_diagnostic.csv`
- `trailing_silence_raw_processed_audit.csv`
- `trailing_silence_market_wide_audit.csv`
- `trailing_silence_final_findings.csv`
- `trailing_silence_market_month_findings.csv`

Relevant scripts:

- `analyze_trailing_reporting_silence.py`
- `reconcile_trailing_silence_raw_processed.py`
- `classify_trailing_silence_market_activity.py`
- `build_trailing_silence_final_findings.py`

**Report status:** Based on the verified analysis outputs available on 11 November 2026.
