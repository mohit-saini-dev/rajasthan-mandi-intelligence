import pandas as pd

CONSISTENCY_PATH = "data/processed/market_reporting_consistency.csv"
PANEL_PATH = "data/processed/monthly_reporting_pair_month_panel.csv"

MONTHLY_OUTPUT = "data/processed/low_reporting_monthly_peer_comparison.csv"
SEASONAL_OUTPUT = "data/processed/low_reporting_seasonal_peer_comparison.csv"

TOP_N = 15

keys = ["Market_Id", "Commodity_Id"]
period_keys = ["Commodity_Name", "Year", "Month_Num"]

consistency = pd.read_csv(CONSISTENCY_PATH)
panel = pd.read_csv(PANEL_PATH)

# Select the 15 lowest adjusted reporting indices.
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

# Validate the full pair-month panel.
panel_key = keys + ["Year", "Month_Num"]

if panel.duplicated(panel_key).any():
    raise ValueError("Duplicate pair-month records detected.")

if (panel["Expected_Pair_Days"] <= 0).any():
    raise ValueError("Non-positive expected pair-days detected.")

if (
    (panel["Reported_Pair_Days"] < 0)
    | (panel["Reported_Pair_Days"] > panel["Expected_Pair_Days"])
).any():
    raise ValueError("Invalid reported pair-day counts detected.")

# Exclude incomplete November 2026.
complete = panel[
    ~((panel["Year"] == 2026) & (panel["Month_Num"] == 11))
].copy()

# Calculate totals across all eligible pairs for each crop/year/month.
peer_totals = (
    complete.groupby(period_keys)
    .agg(
        Commodity_Reported_Days=("Reported_Pair_Days", "sum"),
        Commodity_Expected_Days=("Expected_Pair_Days", "sum"),
        Commodity_Pair_Count=("Market_Id", "nunique"),
    )
    .reset_index()
)

# Attach commodity/year/month totals to each pair-month.
comparison = complete.merge(
    peer_totals,
    on=period_keys,
    how="left",
    validate="many_to_one"
)

# Leave-one-pair-out peer benchmark.
comparison["Peer_Reported_Days"] = (
    comparison["Commodity_Reported_Days"]
    - comparison["Reported_Pair_Days"]
)

comparison["Peer_Expected_Days"] = (
    comparison["Commodity_Expected_Days"]
    - comparison["Expected_Pair_Days"]
)

comparison["Peer_Pair_Count"] = (
    comparison["Commodity_Pair_Count"] - 1
)

if (comparison["Peer_Expected_Days"] <= 0).any():
    raise ValueError("Non-positive peer denominator detected.")

comparison["Pair_Monthly_Rate_Pct"] = (
    comparison["Reported_Pair_Days"]
    / comparison["Expected_Pair_Days"]
    * 100
)

comparison["Peer_Monthly_Rate_Pct"] = (
    comparison["Peer_Reported_Days"]
    / comparison["Peer_Expected_Days"]
    * 100
)

comparison["Adjusted_Gap_Pct_Points"] = (
    comparison["Pair_Monthly_Rate_Pct"]
    - comparison["Peer_Monthly_Rate_Pct"]
)

comparison["Adjusted_Monthly_Index_Pct"] = (
    comparison["Pair_Monthly_Rate_Pct"]
    / comparison["Peer_Monthly_Rate_Pct"].replace(0, float("nan"))
    * 100
)

comparison["Peer_Expected_Reported_Days"] = (
    comparison["Expected_Pair_Days"]
    * comparison["Peer_Monthly_Rate_Pct"]
    / 100
)

# Retain only the 15 selected pairs.
selected = comparison.merge(
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
    raise ValueError("Duplicate selected pair-month records detected.")

selected = selected.sort_values(
    ["Commodity_Name", "Market_Name", "Year", "Month_Num"]
)

# Aggregate comparable months across years for each selected pair.
seasonal = (
    selected.groupby(
        keys + ["Commodity_Name", "Market_Name", "Month_Num", "Month"]
    )
    .agg(
        Years_Compared=("Year", "nunique"),
        Expected_Pair_Days=("Expected_Pair_Days", "sum"),
        Reported_Pair_Days=("Reported_Pair_Days", "sum"),
        Peer_Expected_Reported_Days=(
            "Peer_Expected_Reported_Days", "sum"
        ),
        Peer_Expected_Days=("Peer_Expected_Days", "sum"),
        Peer_Reported_Days=("Peer_Reported_Days", "sum"),
        Minimum_Peer_Pairs=("Peer_Pair_Count", "min"),
    )
    .reset_index()
)

seasonal["Seasonal_Reporting_Rate_Pct"] = (
    seasonal["Reported_Pair_Days"]
    / seasonal["Expected_Pair_Days"]
    * 100
)

seasonal["Seasonal_Peer_Benchmark_Pct"] = (
    seasonal["Peer_Expected_Reported_Days"]
    / seasonal["Expected_Pair_Days"]
    * 100
)

seasonal["Seasonal_Adjusted_Gap_Pct_Points"] = (
    seasonal["Seasonal_Reporting_Rate_Pct"]
    - seasonal["Seasonal_Peer_Benchmark_Pct"]
)

seasonal["Seasonal_Adjusted_Index_Pct"] = (
    seasonal["Seasonal_Reporting_Rate_Pct"]
    / seasonal["Seasonal_Peer_Benchmark_Pct"].replace(0, float("nan"))
    * 100
)

# Save outputs.
selected.to_csv(MONTHLY_OUTPUT, index=False)
seasonal.to_csv(SEASONAL_OUTPUT, index=False)

print("Selected pairs:", selected[keys].drop_duplicates().shape[0])
print("Monthly comparison rows:", len(selected))
print("Seasonal comparison rows:", len(seasonal))

print("\n--- Lowest 15 pair-month adjusted indices ---")
print(
    selected[
        [
            "Commodity_Name",
            "Market_Name",
            "Year",
            "Month",
            "Pair_Monthly_Rate_Pct",
            "Peer_Monthly_Rate_Pct",
            "Adjusted_Gap_Pct_Points",
            "Adjusted_Monthly_Index_Pct",
            "Peer_Pair_Count",
        ]
    ]
    .sort_values("Adjusted_Monthly_Index_Pct")
    .head(15)
    .to_string(index=False)
)

print("\n--- Seasonal peer comparison ---")
seasonal_pivot = seasonal.pivot(
    index=["Commodity_Name", "Market_Name"],
    columns="Month_Num",
    values="Seasonal_Adjusted_Index_Pct"
)

print(seasonal_pivot.round(1).to_string())

print("\nSaved:")
print(MONTHLY_OUTPUT)
print(SEASONAL_OUTPUT)
