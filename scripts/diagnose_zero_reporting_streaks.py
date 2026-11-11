import pandas as pd

CONSISTENCY_PATH = "data/processed/market_reporting_consistency.csv"
PANEL_PATH = "data/processed/monthly_reporting_pair_month_panel.csv"

MONTHLY_OUTPUT = "data/processed/zero_reporting_monthly_diagnostic.csv"
YEARLY_OUTPUT = "data/processed/zero_reporting_yearly_diagnostic.csv"
SUMMARY_OUTPUT = "data/processed/zero_reporting_streak_summary.csv"

TOP_N = 15
PEER_ACTIVITY_THRESHOLD_PCT = 20.0

keys = ["Market_Id", "Commodity_Id"]
period_keys = ["Commodity_Name", "Year", "Month_Num"]

consistency = pd.read_csv(CONSISTENCY_PATH)
panel = pd.read_csv(PANEL_PATH)

# Select the 15 lowest adjusted reporting-index pairs.
top_pairs = (
    consistency.sort_values("Adjusted_Reporting_Index_Pct")
    .head(TOP_N)
    .copy()
)

for df in [top_pairs, panel]:
    df["Market_Id"] = pd.to_numeric(
        df["Market_Id"], errors="raise"
    ).astype(int)

    df["Commodity_Id"] = pd.to_numeric(
        df["Commodity_Id"], errors="raise"
    ).astype(int)

# Exclude incomplete November 2026.
complete = panel[
    ~((panel["Year"] == 2026) & (panel["Month_Num"] == 11))
].copy()

panel_key = keys + ["Year", "Month_Num"]

if complete.duplicated(panel_key).any():
    raise ValueError("Duplicate pair-month records detected.")

if (complete["Expected_Pair_Days"] <= 0).any():
    raise ValueError("Non-positive expected pair-days detected.")

if (
    (complete["Reported_Pair_Days"] < 0)
    | (complete["Reported_Pair_Days"] > complete["Expected_Pair_Days"])
).any():
    raise ValueError("Invalid reported pair-day counts detected.")

# Calculate crop-month peer totals.
peer_totals = (
    complete.groupby(period_keys)
    .agg(
        Commodity_Reported_Days=("Reported_Pair_Days", "sum"),
        Commodity_Expected_Days=("Expected_Pair_Days", "sum"),
        Commodity_Pair_Count=("Market_Id", "nunique"),
    )
    .reset_index()
)

monthly = complete.merge(
    peer_totals,
    on=period_keys,
    how="left",
    validate="many_to_one"
)

# Leave-one-pair-out peer benchmark.
monthly["Peer_Reported_Days"] = (
    monthly["Commodity_Reported_Days"]
    - monthly["Reported_Pair_Days"]
)

monthly["Peer_Expected_Days"] = (
    monthly["Commodity_Expected_Days"]
    - monthly["Expected_Pair_Days"]
)

if (monthly["Peer_Expected_Days"] <= 0).any():
    raise ValueError("Non-positive peer denominator detected.")

monthly["Pair_Monthly_Rate_Pct"] = (
    monthly["Reported_Pair_Days"]
    / monthly["Expected_Pair_Days"]
    * 100
)

monthly["Peer_Monthly_Rate_Pct"] = (
    monthly["Peer_Reported_Days"]
    / monthly["Peer_Expected_Days"]
    * 100
)

monthly["Zero_Reporting_Month"] = (
    monthly["Reported_Pair_Days"] == 0
)

monthly["Peer_Active_Zero_Month"] = (
    monthly["Zero_Reporting_Month"]
    & (
        monthly["Peer_Monthly_Rate_Pct"]
        >= PEER_ACTIVITY_THRESHOLD_PCT
    )
)

monthly["Below_Peer_Benchmark"] = (
    monthly["Pair_Monthly_Rate_Pct"]
    < monthly["Peer_Monthly_Rate_Pct"]
)

# Retain the selected 15 pairs.
selected = monthly.merge(
    top_pairs[
        keys + [
            "Market_Name",
            "Adjusted_Reporting_Index_Pct",
        ]
    ],
    on=keys,
    how="inner",
    validate="many_to_one"
)

if selected.duplicated(panel_key).any():
    raise ValueError("Duplicate selected pair-month rows detected.")

# Calculate consecutive zero-month streaks chronologically.
selected["Month_Index"] = (
    selected["Year"] * 12 + selected["Month_Num"]
)

selected = selected.sort_values(
    keys + ["Month_Index"]
)

def longest_streak(values):
    longest = 0
    current = 0

    for value in values:
        if bool(value):
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest

summary_rows = []

for (market_id, commodity_id), group in selected.groupby(keys):
    group = group.sort_values("Month_Index")

    summary_rows.append({
        "Market_Id": market_id,
        "Commodity_Id": commodity_id,
        "Market_Name": group["Market_Name"].iloc[0],
        "Commodity_Name": group["Commodity_Name"].iloc[0],
        "Adjusted_Reporting_Index_Pct":
            group["Adjusted_Reporting_Index_Pct"].iloc[0],
        "Months_Examined": len(group),
        "Zero_Reporting_Months":
            int(group["Zero_Reporting_Month"].sum()),
        "Peer_Active_Zero_Months":
            int(group["Peer_Active_Zero_Month"].sum()),
        "Months_Below_Peer_Benchmark":
            int(group["Below_Peer_Benchmark"].sum()),
        "Longest_Zero_Month_Streak":
            longest_streak(group["Zero_Reporting_Month"]),
        "Longest_Peer_Active_Zero_Streak":
            longest_streak(group["Peer_Active_Zero_Month"]),
        "Mean_Peer_Monthly_Rate_Pct":
            group["Peer_Monthly_Rate_Pct"].mean(),
        "Mean_Pair_Monthly_Rate_Pct":
            group["Pair_Monthly_Rate_Pct"].mean(),
    })

summary = pd.DataFrame(summary_rows)

# Year-by-year profile.
yearly = (
    selected.groupby(
        keys + ["Market_Name", "Commodity_Name", "Year"]
    )
    .agg(
        Months_Examined=("Month_Num", "nunique"),
        Expected_Pair_Days=("Expected_Pair_Days", "sum"),
        Reported_Pair_Days=("Reported_Pair_Days", "sum"),
        Zero_Reporting_Months=("Zero_Reporting_Month", "sum"),
        Peer_Active_Zero_Months=("Peer_Active_Zero_Month", "sum"),
        Months_Below_Peer=("Below_Peer_Benchmark", "sum"),
    )
    .reset_index()
)

yearly["Yearly_Reporting_Rate_Pct"] = (
    yearly["Reported_Pair_Days"]
    / yearly["Expected_Pair_Days"]
    * 100
)

# Add a year-level peer reporting rate using all eligible pairs.
yearly_peer = (
    complete.groupby(["Commodity_Name", "Year"])
    .agg(
        All_Pair_Reported_Days=("Reported_Pair_Days", "sum"),
        All_Pair_Expected_Days=("Expected_Pair_Days", "sum"),
    )
    .reset_index()
)

yearly = yearly.merge(
    yearly_peer,
    on=["Commodity_Name", "Year"],
    how="left",
    validate="many_to_one"
)

yearly["Peer_Reporting_Rate_Pct"] = (
    (
        yearly["All_Pair_Reported_Days"]
        - yearly["Reported_Pair_Days"]
    )
    /
    (
        yearly["All_Pair_Expected_Days"]
        - yearly["Expected_Pair_Days"]
    )
    * 100
)

yearly["Yearly_Gap_Pct_Points"] = (
    yearly["Yearly_Reporting_Rate_Pct"]
    - yearly["Peer_Reporting_Rate_Pct"]
)

# Sort and save.
selected = selected.sort_values(
    ["Commodity_Name", "Market_Name", "Year", "Month_Num"]
)

yearly = yearly.sort_values(
    ["Commodity_Name", "Market_Name", "Year"]
)

summary = summary.sort_values(
    ["Peer_Active_Zero_Months", "Longest_Peer_Active_Zero_Streak",
     "Adjusted_Reporting_Index_Pct"],
    ascending=[False, False, True]
)

selected.to_csv(MONTHLY_OUTPUT, index=False)
yearly.to_csv(YEARLY_OUTPUT, index=False)
summary.to_csv(SUMMARY_OUTPUT, index=False)

print("Selected pairs:", len(summary))
print("Monthly diagnostic rows:", len(selected))
print("Yearly diagnostic rows:", len(yearly))
print(
    "Months excluded: November 2026 (incomplete)"
)

print("\n--- Zero-reporting streak summary ---")
print(
    summary[
        [
            "Commodity_Name",
            "Market_Name",
            "Months_Examined",
            "Zero_Reporting_Months",
            "Peer_Active_Zero_Months",
            "Longest_Zero_Month_Streak",
            "Longest_Peer_Active_Zero_Streak",
            "Adjusted_Reporting_Index_Pct",
        ]
    ].to_string(index=False)
)

print("\n--- Year-by-year profile ---")
print(
    yearly[
        [
            "Commodity_Name",
            "Market_Name",
            "Year",
            "Yearly_Reporting_Rate_Pct",
            "Peer_Reporting_Rate_Pct",
            "Yearly_Gap_Pct_Points",
            "Zero_Reporting_Months",
            "Peer_Active_Zero_Months",
        ]
    ].to_string(index=False)
)

print("\nSaved:")
print(MONTHLY_OUTPUT)
print(YEARLY_OUTPUT)
print(SUMMARY_OUTPUT)
