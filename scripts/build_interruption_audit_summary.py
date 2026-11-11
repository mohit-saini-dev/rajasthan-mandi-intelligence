from pathlib import Path
import pandas as pd

input_path = Path("data/processed/interruption_monthly_raw_processed_audit.csv")
summary_path = Path("data/processed/interruption_audit_summary.csv")
report_path = Path("reports/source_level_reporting_interruption_audit.md")

if not input_path.exists():
    raise FileNotFoundError(f"Required audit file not found: {input_path}")

monthly = pd.read_csv(input_path)

required = {
    "Market", "Month", "Raw_Rows", "Raw_Active_Dates",
    "Raw_Commodity_Date_Pairs", "Processed_Rows",
    "Processed_Active_Dates",
}
missing = required - set(monthly.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

targets = [
    {
        "Market": "Osiyan Mathania APMC",
        "Expected_Months": 17,
        "Classification": "Source-level prolonged silence",
        "Interpretation": (
            "No exact-label records in the raw exports during "
            "February 2023 through June 2024."
        ),
    },
    {
        "Market": "Barisadri APMC",
        "Expected_Months": 15,
        "Classification": "Source-level prolonged silence",
        "Interpretation": (
            "No exact-label records in the raw exports during "
            "April 2023 through June 2024."
        ),
    },
    {
        "Market": "HanumangarhTown APMC",
        "Expected_Months": 6,
        "Classification": "Exact-label source-level silence",
        "Interpretation": (
            "No exact-label records during May through October 2025. "
            "Other Hanumangarh market labels are treated as distinct."
        ),
    },
    {
        "Market": "Kotputli APMC",
        "Expected_Months": 8,
        "Classification": "Intermittent source reporting",
        "Interpretation": (
            "Raw records occur in September and November 2025, "
            "with no records in the other audited months."
        ),
    },
]

summary_rows = []

for target in targets:
    market = target["Market"]
    part = monthly[monthly["Market"].eq(market)].copy()

    if len(part) != target["Expected_Months"]:
        raise ValueError(
            f"{market}: expected {target['Expected_Months']} monthly rows, "
            f"found {len(part)}."
        )

    if part["Month"].duplicated().any():
        raise ValueError(f"{market}: duplicate months found.")

    raw_rows = int(part["Raw_Rows"].sum())
    processed_rows = int(part["Processed_Rows"].sum())
    raw_active_months = int((part["Raw_Active_Dates"] > 0).sum())
    processed_active_months = int((part["Processed_Active_Dates"] > 0).sum())

    row_counts_match = bool(
        (part["Raw_Rows"].to_numpy() ==
         part["Processed_Rows"].to_numpy()).all()
    )
    active_dates_match = bool(
        (part["Raw_Active_Dates"].to_numpy() ==
         part["Processed_Active_Dates"].to_numpy()).all()
    )

    if not row_counts_match or not active_dates_match:
        raise ValueError(
            f"{market}: raw and processed monthly counts do not match."
        )

    summary_rows.append({
        "Market": market,
        "Classification": target["Classification"],
        "Audited_Months": len(part),
        "Raw_Rows": raw_rows,
        "Processed_Rows": processed_rows,
        "Raw_Active_Months": raw_active_months,
        "Processed_Active_Months": processed_active_months,
        "Raw_Active_Dates": int(part["Raw_Active_Dates"].sum()),
        "Processed_Active_Dates": int(part["Processed_Active_Dates"].sum()),
        "Raw_Commodity_Date_Pairs": int(
            part["Raw_Commodity_Date_Pairs"].sum()
        ),
        "Monthly_Row_Counts_Match": row_counts_match,
        "Monthly_Active_Date_Counts_Match": active_dates_match,
        "Interpretation": target["Interpretation"],
    })

summary = pd.DataFrame(summary_rows)

summary_path.parent.mkdir(parents=True, exist_ok=True)
report_path.parent.mkdir(parents=True, exist_ok=True)

summary.to_csv(summary_path, index=False)

lines = [
    "# Source-Level Reporting Interruption Audit",
    "",
    "## Objective",
    "",
    "Determine whether selected market reporting interruptions are "
    "already present in the downloaded AGMARKNET raw exports or were "
    "introduced during processing.",
    "",
    "## Method",
    "",
    "- Read the monthly raw-versus-processed reconciliation output.",
    "- Match markets using their exact market labels after trimming "
    "outer whitespace and case-folding.",
    "- Compare monthly raw and processed row counts and active-date counts.",
    "- Keep similarly named market labels separate unless identity is "
    "independently established.",
    "",
    "## Results",
    "",
    "| Market | Classification | Audited months | Raw rows | Processed rows | "
    "Raw active months | Processed active months |",
    "|---|---|---:|---:|---:|---:|---:|",
]

for row in summary.to_dict("records"):
    lines.append(
        f"| {row['Market']} | {row['Classification']} "
        f"| {row['Audited_Months']} | {row['Raw_Rows']} "
        f"| {row['Processed_Rows']} | {row['Raw_Active_Months']} "
        f"| {row['Processed_Active_Months']} |"
    )

lines += [
    "",
    "## Market-level findings",
    "",
]

for target, row in zip(targets, summary.to_dict("records")):
    lines += [
        f"### {target['Market']}",
        "",
        target["Interpretation"],
        "",
        f"- Raw rows: {row['Raw_Rows']}",
        f"- Processed rows: {row['Processed_Rows']}",
        f"- Raw active months: {row['Raw_Active_Months']} "
        f"of {row['Audited_Months']}",
        f"- Processed active months: {row['Processed_Active_Months']} "
        f"of {row['Audited_Months']}",
        f"- Monthly row counts match: {row['Monthly_Row_Counts_Match']}",
        f"- Monthly active-date counts match: "
        f"{row['Monthly_Active_Date_Counts_Match']}",
        "",
    ]

lines += [
    "## Overall conclusion",
    "",
    "For all four audited market-periods, monthly raw and processed row "
    "counts and active-date counts match. The observed absences were "
    "already present in the downloaded raw exports. This audit found no "
    "evidence that the processing pipeline introduced these specific "
    "reporting interruptions.",
    "",
    "## Limitations",
    "",
    "- Source-level silence means that records are absent from the "
    "downloaded raw exports. It does not establish physical market "
    "closure, non-operation, or an AGMARKNET system outage.",
    "- Exact market labels are kept separate. In particular, "
    "`HanumangarhTown APMC`, `Hanumangarh Town APMC`, and "
    "`Hanumangarh APMC` are not assumed to be the same entity.",
    "- Raw row counts are counts across the downloaded files. If raw "
    "exports overlap, duplicate source rows may exist.",
    "- This is a targeted audit of four selected market-periods, not "
    "a complete reconciliation of every market and date in the dataset.",
    "",
    "## Reproducibility",
    "",
    f"Input: `{input_path.as_posix()}`",
    "",
    f"Summary output: `{summary_path.as_posix()}`",
    "",
]

report_path.write_text("\n".join(lines), encoding="utf-8")

print("Audit summary:")
print(summary.to_string(index=False))
print("\nSaved:")
print(summary_path)
print(report_path)
