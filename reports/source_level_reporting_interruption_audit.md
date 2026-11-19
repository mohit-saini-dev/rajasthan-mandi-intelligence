# Source-Level Reporting Interruption Audit

## Objective

Determine whether selected market reporting interruptions are already present in the downloaded AGMARKNET raw exports or were introduced during processing.

## Method

- Read the monthly raw-versus-processed reconciliation output.
- Match markets using their exact market labels after trimming outer whitespace and case-folding.
- Compare monthly raw and processed row counts and active-date counts.
- Keep similarly named market labels separate unless identity is independently established.

## Results

| Market | Classification | Audited months | Raw rows | Processed rows | Raw active months | Processed active months |
|---|---|---:|---:|---:|---:|---:|
| Osiyan Mathania APMC | Source-level prolonged silence | 17 | 0 | 0 | 0 | 0 |
| Barisadri APMC | Source-level prolonged silence | 15 | 0 | 0 | 0 | 0 |
| HanumangarhTown APMC | Exact-label source-level silence | 6 | 0 | 0 | 0 | 0 |
| Kotputli APMC | Intermittent source reporting | 8 | 10 | 10 | 2 | 2 |

## Market-level findings

### Osiyan Mathania APMC

No exact-label records in the raw exports during February 2023 through June 2024.

- Raw rows: 0
- Processed rows: 0
- Raw active months: 0 of 17
- Processed active months: 0 of 17
- Monthly row counts match: True
- Monthly active-date counts match: True

### Barisadri APMC

No exact-label records in the raw exports during April 2023 through June 2024.

- Raw rows: 0
- Processed rows: 0
- Raw active months: 0 of 15
- Processed active months: 0 of 15
- Monthly row counts match: True
- Monthly active-date counts match: True

### HanumangarhTown APMC

No exact-label records during May through October 2025. Other Hanumangarh market labels are treated as distinct.

- Raw rows: 0
- Processed rows: 0
- Raw active months: 0 of 6
- Processed active months: 0 of 6
- Monthly row counts match: True
- Monthly active-date counts match: True

### Kotputli APMC

Raw records occur in September and November 2025, with no records in the other audited months.

- Raw rows: 10
- Processed rows: 10
- Raw active months: 2 of 8
- Processed active months: 2 of 8
- Monthly row counts match: True
- Monthly active-date counts match: True

## Overall conclusion

For all four audited market-periods, monthly raw and processed row counts and active-date counts match. The observed absences were already present in the downloaded raw exports. This audit found no evidence that the processing pipeline introduced these specific reporting interruptions.

## Limitations

- Source-level silence means that records are absent from the downloaded raw exports. It does not establish physical market closure, non-operation, or an AGMARKNET system outage.
- Exact market labels are kept separate. In particular, `HanumangarhTown APMC`, `Hanumangarh Town APMC`, and `Hanumangarh APMC` are not assumed to be the same entity.
- Raw row counts are counts across the downloaded files. If raw exports overlap, duplicate source rows may exist.
- This is a targeted audit of four selected market-periods, not a complete reconciliation of every market and date in the dataset.

## Reproducibility

Input: `data/processed/interruption_monthly_raw_processed_audit.csv`

Summary output: `data/processed/interruption_audit_summary.csv`
