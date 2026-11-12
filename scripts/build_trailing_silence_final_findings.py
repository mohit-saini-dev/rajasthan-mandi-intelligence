from pathlib import Path

import pandas as pd


base = Path("data/processed")

summary = pd.read_csv(
    base / "trailing_silence_summary.csv"
)

reconciliation = pd.read_csv(
    base / "trailing_silence_raw_processed_audit.csv"
)

market_activity = pd.read_csv(
    base / "trailing_silence_market_wide_audit.csv"
)

keys = ["Market_Id", "Commodity_Id"]


# Validate required reconciliation columns.
required_reconciliation = {
    *keys,
    "Month",
    "Raw_Rows",
    "Processed_Rows",
    "Raw_Active_Dates",
    "Processed_Active_Dates",
    "Row_Counts_Match",
    "Active_Date_Counts_Match",
    "Raw_Source_Records_Present",
    "Processed_Records_Present",
}

missing = required_reconciliation - set(reconciliation.columns)

if missing:
    raise ValueError(
        f"Missing reconciliation columns: {sorted(missing)}"
    )


# Validate required market activity columns.
required_activity = {
    *keys,
    "Market_Name",
    "Month",
    "Classification",
    "Market_Raw_Rows_All_Commodities",
    "Market_Active_Dates_All_Commodities",
    "Active_Commodities",
    "Commodity_Name",
}

missing = required_activity - set(market_activity.columns)

if missing:
    raise ValueError(
        f"Missing market activity columns: {sorted(missing)}"
    )


# Validate source-level grain.
if summary.duplicated(keys).any():
    raise ValueError(
        "Duplicate market-commodity pairs in summary."
    )

if reconciliation.duplicated(keys + ["Month"]).any():
    raise ValueError(
        "Duplicate pair-month rows in reconciliation."
    )

if market_activity.duplicated(keys + ["Month"]).any():
    raise ValueError(
        "Duplicate pair-month rows in market activity."
    )


# Aggregate reconciliation checks at market-commodity level.
reconciliation_counts = (
    reconciliation.groupby(keys, as_index=False)
    .agg(
        Audited_Trailing_Months=("Month", "nunique"),
        Raw_Active_Trailing_Months=(
            "Raw_Source_Records_Present",
            "sum",
        ),
        Processed_Active_Trailing_Months=(
            "Processed_Records_Present",
            "sum",
        ),
        Row_Count_Matches=(
            "Row_Counts_Match",
            "sum",
        ),
        Active_Date_Count_Matches=(
            "Active_Date_Counts_Match",
            "sum",
        ),
    )
)


# Aggregate commodity-level source-silence classifications.
market_counts = (
    market_activity.groupby(keys, as_index=False)
    .agg(
        Commodity_Specific_Months=(
            "Classification",
            lambda s: (
                s == "Commodity-specific source silence"
            ).sum(),
        ),
        Potentially_Market_Wide_Months=(
            "Classification",
            lambda s: (
                s == "Potentially market-wide source silence"
            ).sum(),
        ),
    )
)


# Combine pair-level findings.
findings = (
    summary
    .merge(
        reconciliation_counts,
        on=keys,
        how="left",
        validate="one_to_one",
    )
    .merge(
        market_counts,
        on=keys,
        how="left",
        validate="one_to_one",
    )
)


# Normalize count columns.
count_columns = [
    "Audited_Trailing_Months",
    "Raw_Active_Trailing_Months",
    "Processed_Active_Trailing_Months",
    "Row_Count_Matches",
    "Active_Date_Count_Matches",
    "Commodity_Specific_Months",
    "Potentially_Market_Wide_Months",
]

for column in count_columns:
    findings[column] = (
        findings[column]
        .fillna(0)
        .astype(int)
    )


# Determine reconciliation status.
findings["Reconciliation_Status"] = "REVIEW"

not_applicable = findings["Audited_Trailing_Months"].eq(0)

findings.loc[
    not_applicable,
    "Reconciliation_Status",
] = "NOT APPLICABLE"


passed = (
    findings["Audited_Trailing_Months"].gt(0)
    & findings["Row_Count_Matches"].eq(
        findings["Audited_Trailing_Months"]
    )
    & findings["Active_Date_Count_Matches"].eq(
        findings["Audited_Trailing_Months"]
    )
)

findings.loc[
    passed,
    "Reconciliation_Status",
] = "PASS"


# Describe the pair-level source-silence finding.
findings["Finding"] = findings.apply(
    lambda row:
        "No trailing silence observed at dataset cutoff"
        if row["Audited_Trailing_Months"] == 0
        else (
            "Potentially market-wide source silence detected"
            if row["Potentially_Market_Wide_Months"] > 0
            else "Commodity-specific source silence only"
        ),
    axis=1,
)


# Save pair-level findings.
pair_output = (
    base / "trailing_silence_final_findings.csv"
)

findings.to_csv(pair_output, index=False)


# Validate market-level values before aggregation.
market_level_columns = [
    "Market_Raw_Rows_All_Commodities",
    "Market_Active_Dates_All_Commodities",
    "Active_Commodities",
]

market_level_consistency = (
    market_activity.groupby(
        ["Market_Id", "Market_Name", "Month"]
    )[market_level_columns]
    .nunique(dropna=False)
)

if market_level_consistency.gt(1).any().any():
    raise ValueError(
        "Inconsistent market-level activity values across "
        "commodity rows for the same market-month."
    )


# Preserve disagreement between commodity-level classifications.
market_month = (
    market_activity.groupby(
        ["Market_Id", "Market_Name", "Month"],
        as_index=False,
    )
    .agg(
        Market_Raw_Rows_All_Commodities=(
            "Market_Raw_Rows_All_Commodities",
            "first",
        ),
        Market_Active_Dates_All_Commodities=(
            "Market_Active_Dates_All_Commodities",
            "first",
        ),
        Active_Commodities=(
            "Active_Commodities",
            "first",
        ),
        Pair_Months_Audited=(
            "Commodity_Id",
            "nunique",
        ),
        Target_Commodities_Audited=(
            "Commodity_Name",
            lambda s: "; ".join(sorted(set(s))),
        ),
        Classification_Count=(
            "Classification",
            "nunique",
        ),
        Classifications=(
            "Classification",
            lambda s: "; ".join(sorted(set(s))),
        ),
    )
)


# Assign a single classification or preserve mixed results.
market_month["Classification"] = market_month.apply(
    lambda row:
        row["Classifications"]
        if row["Classification_Count"] == 1
        else "Mixed",
    axis=1,
)


# Save market-month findings.
market_output = (
    base / "trailing_silence_market_month_findings.csv"
)

market_month.to_csv(market_output, index=False)


# Display pair-level findings.
display_columns = [
    "Market_Name",
    "Commodity_Name",
    "Last_Reported_Date",
    "Audited_Trailing_Months",
    "Row_Count_Matches",
    "Active_Date_Count_Matches",
    "Reconciliation_Status",
    "Finding",
]

print("--- Pair-level findings ---")

print(
    findings[display_columns].to_string(index=False)
)


# Display reconciliation status.
print("\n--- Reconciliation status ---")

print(
    findings["Reconciliation_Status"]
    .value_counts()
    .to_string()
)


# Display market-month classifications.
print("\n--- Market-month classifications ---")

print(
    market_month["Classification"]
    .value_counts()
    .to_string()
)


# Report whether all applicable reconciliations passed.
applicable = findings[
    findings["Reconciliation_Status"] != "NOT APPLICABLE"
]

all_passed = (
    not applicable.empty
    and applicable["Reconciliation_Status"].eq("PASS").all()
)

print(
    "\nAll applicable reconciliations passed:",
    bool(all_passed),
)

if not all_passed:
    raise RuntimeError(
        "One or more applicable trailing-silence "
        "reconciliations require review."
    )


print("\nSaved:")
print(pair_output)
print(market_output)
