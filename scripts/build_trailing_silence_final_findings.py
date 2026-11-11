from pathlib import Path
import pandas as pd

base = Path("data/processed")

summary = pd.read_csv(base / "trailing_silence_summary.csv")
reconciliation = pd.read_csv(
    base / "trailing_silence_raw_processed_audit.csv"
)
market_activity = pd.read_csv(
    base / "trailing_silence_market_wide_audit.csv"
)

keys = ["Market_Id", "Commodity_Id"]

if summary.duplicated(keys).any():
    raise ValueError("Duplicate market-commodity pairs in summary.")

reconciliation_counts = (
    reconciliation.groupby(keys, as_index=False)
    .agg(
        Audited_Trailing_Months=("Month", "nunique"),
        Raw_Active_Trailing_Months=("Raw_Source_Records_Present", "sum"),
        Processed_Active_Trailing_Months=(
            "Processed_Records_Present", "sum"
        ),
        Reconciliation_Month_Count_Matches=(
            "Active_Date_Counts_Match", "sum"
        ),
    )
)

market_counts = (
    market_activity.groupby(keys, as_index=False)
    .agg(
        Commodity_Specific_Months=(
            "Classification",
            lambda s: (s == "Commodity-specific source silence").sum()
        ),
        Potentially_Market_Wide_Months=(
            "Classification",
            lambda s: (
                s == "Potentially market-wide source silence"
            ).sum()
        ),
    )
)

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

findings["Audited_Trailing_Months"] = (
    findings["Audited_Trailing_Months"].fillna(0).astype(int)
)

findings["Reconciliation_Month_Count_Matches"] = (
    findings["Reconciliation_Month_Count_Matches"].fillna(0).astype(int)
)

findings["Reconciliation_Status"] = "PASS"

findings.loc[
    findings["Audited_Trailing_Months"] == 0,
    "Reconciliation_Status"
] = "NOT APPLICABLE"

findings.loc[
    (
        findings["Audited_Trailing_Months"] > 0
    )
    & (
        findings["Audited_Trailing_Months"]
        != findings["Reconciliation_Month_Count_Matches"]
    ),
    "Reconciliation_Status"
] = "REVIEW"

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

pair_output = base / "trailing_silence_final_findings.csv"
findings.to_csv(pair_output, index=False)

market_month = (
    market_activity.groupby(
        ["Market_Id", "Market_Name", "Month"],
        as_index=False,
    )
    .agg(
        Market_Raw_Rows_All_Commodities=(
            "Market_Raw_Rows_All_Commodities", "first"
        ),
        Market_Active_Dates_All_Commodities=(
            "Market_Active_Dates_All_Commodities", "first"
        ),
        Active_Commodities=("Active_Commodities", "first"),
        Pair_Months_Audited=("Commodity_Id", "count"),
        Target_Commodities_Audited=(
            "Commodity_Name",
            lambda s: "; ".join(sorted(set(s)))
        ),
        Classification=("Classification", "first"),
    )
)

market_output = base / "trailing_silence_market_month_findings.csv"
market_month.to_csv(market_output, index=False)

print("--- Pair-level findings ---")
print(findings[
    [
        "Market_Name", "Commodity_Name", "Last_Reported_Date",
        "Audited_Trailing_Months", "Reconciliation_Status", "Finding"
    ]
].to_string(index=False))

print("\n--- Integrity checks ---")
print("Selected pairs:", len(findings))
print("Pair-month records:", len(market_activity))
print("\nReconciliation status:")
print(findings["Reconciliation_Status"].value_counts().to_string())
print(
    "All applicable reconciliations passed:",
    bool(
        (
            findings.loc[
                findings["Reconciliation_Status"] != "NOT APPLICABLE",
                "Reconciliation_Status"
            ] == "PASS"
        ).all()
    )
)
print(
    "Market-wide source-silence pair-months:",
    int(
        (
            market_activity["Classification"]
            == "Potentially market-wide source silence"
        ).sum()
    ),
)

print("\nSaved:")
print(pair_output)
print(market_output)
