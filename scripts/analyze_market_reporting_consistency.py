import pandas as pd

PAIR_INPUT = "data/processed/commodity_weekday_reporting_by_pair.csv"
MARKET_INPUT = "data/processed/dim_market.csv"

PAIR_OUTPUT = "data/processed/market_reporting_consistency.csv"
SUMMARY_OUTPUT = "data/processed/market_reporting_consistency_summary.csv"

pair = pd.read_csv(PAIR_INPUT)
markets = pd.read_csv(MARKET_INPUT)

required_columns = [
    "Market_Id",
    "Commodity_Id",
    "Commodity_Name",
    "Weekday",
    "Total_Reported",
    "Total_Expected",
    "Pair_Reporting_Rate_Pct",
]

missing_columns = [
    col for col in required_columns if col not in pair.columns
]

if missing_columns:
    raise ValueError(f"Missing columns in pair input: {missing_columns}")

if not {"Market_Id", "Market_Name"}.issubset(markets.columns):
    raise ValueError("dim_market.csv must contain Market_Id and Market_Name.")

pair_key = ["Market_Id", "Commodity_Id", "Commodity_Name"]

if pair.duplicated(pair_key + ["Weekday"]).any():
    raise ValueError("Duplicate market-commodity-weekday rows detected.")

if (pair["Total_Expected"] <= 0).any():
    raise ValueError("Non-positive expected weekday counts detected.")

# Calculate commodity-wide weekday totals.
weekday_totals = (
    pair.groupby(
        ["Commodity_Name", "Weekday"]
    )
    .agg(
        Commodity_Reported=("Total_Reported", "sum"),
        Commodity_Expected=("Total_Expected", "sum"),
        Commodity_Pairs=("Market_Id", "nunique"),
    )
    .reset_index()
)

pair = pair.merge(
    weekday_totals,
    on=["Commodity_Name", "Weekday"],
    how="left",
    validate="many_to_one"
)

# Leave-one-pair-out peer benchmark for each commodity and weekday.
pair["Peer_Expected"] = (
    pair["Commodity_Expected"] - pair["Total_Expected"]
)

pair["Peer_Reported"] = (
    pair["Commodity_Reported"] - pair["Total_Reported"]
)

if (pair["Peer_Expected"] <= 0).any():
    raise ValueError("Peer benchmark has a non-positive denominator.")

pair["Peer_Weekday_Rate"] = (
    pair["Peer_Reported"] / pair["Peer_Expected"]
)

pair["Pair_Weekday_Rate"] = (
    pair["Total_Reported"] / pair["Total_Expected"]
)

pair["Peer_Expected_Reported"] = (
    pair["Total_Expected"] * pair["Peer_Weekday_Rate"]
)

pair["Below_Peer_Benchmark"] = (
    pair["Pair_Weekday_Rate"] < pair["Peer_Weekday_Rate"]
)

# Aggregate seven weekday comparisons to one row per pair.
consistency = (
    pair.groupby(pair_key)
    .agg(
        Weekdays_Compared=("Weekday", "nunique"),
        Total_Reported_Days=("Total_Reported", "sum"),
        Total_Expected_Days=("Total_Expected", "sum"),
        Peer_Expected_Reported=("Peer_Expected_Reported", "sum"),
        Weekdays_Below_Peer_Benchmark=("Below_Peer_Benchmark", "sum"),
    )
    .reset_index()
)

consistency["Calendar_Span_Reporting_Rate_Pct"] = (
    consistency["Total_Reported_Days"]
    / consistency["Total_Expected_Days"]
    * 100
)

consistency["Peer_Benchmark_Reporting_Rate_Pct"] = (
    consistency["Peer_Expected_Reported"]
    / consistency["Total_Expected_Days"]
    * 100
)

consistency["Adjusted_Gap_Pct_Points"] = (
    consistency["Calendar_Span_Reporting_Rate_Pct"]
    - consistency["Peer_Benchmark_Reporting_Rate_Pct"]
)

consistency["Adjusted_Reporting_Index_Pct"] = (
    consistency["Calendar_Span_Reporting_Rate_Pct"]
    / consistency["Peer_Benchmark_Reporting_Rate_Pct"]
    * 100
)

# Add market names.
consistency = consistency.merge(
    markets[["Market_Id", "Market_Name"]],
    on="Market_Id",
    how="left",
    validate="many_to_one"
)

if consistency["Market_Name"].isna().any():
    raise ValueError("Some Market_Id values did not match dim_market.csv.")

# Rank pairs within each commodity.
consistency["Adjusted_Rank_Within_Commodity"] = (
    consistency.groupby("Commodity_Name")[
        "Adjusted_Reporting_Index_Pct"
    ]
    .rank(method="min", ascending=True)
    .astype(int)
)

consistency["Adjusted_Rank_Percentile"] = (
    consistency.groupby("Commodity_Name")[
        "Adjusted_Reporting_Index_Pct"
    ]
    .rank(method="average", pct=True, ascending=True)
    * 100
)

consistency["Below_Peer_Benchmark"] = (
    consistency["Adjusted_Reporting_Index_Pct"] < 100
)

consistency["Bottom_Quartile_Within_Commodity"] = (
    consistency["Adjusted_Rank_Percentile"] <= 25
)

consistency = consistency.sort_values(
    ["Commodity_Name", "Adjusted_Reporting_Index_Pct"]
)

# Commodity-level overview.
summary = (
    consistency.groupby("Commodity_Name")
    .agg(
        Eligible_Pairs=("Market_Id", "nunique"),
        Mean_Calendar_Span_Rate=(
            "Calendar_Span_Reporting_Rate_Pct", "mean"
        ),
        Median_Calendar_Span_Rate=(
            "Calendar_Span_Reporting_Rate_Pct", "median"
        ),
        Mean_Adjusted_Index=(
            "Adjusted_Reporting_Index_Pct", "mean"
        ),
        Median_Adjusted_Index=(
            "Adjusted_Reporting_Index_Pct", "median"
        ),
        Pairs_Below_Peer_Benchmark=("Below_Peer_Benchmark", "sum"),
        Pairs_In_Bottom_Quartile=(
            "Bottom_Quartile_Within_Commodity", "sum"
        ),
    )
    .reset_index()
)

consistency.to_csv(PAIR_OUTPUT, index=False)
summary.to_csv(SUMMARY_OUTPUT, index=False)

print("Eligible market-commodity pairs:", len(consistency))
print("Commodity summary rows:", len(summary))

print("\n--- Commodity-level consistency summary ---")
print(summary.to_string(index=False))

print("\n--- 15 lowest adjusted reporting indices ---")
print(
    consistency[
        [
            "Commodity_Name",
            "Market_Name",
            "Calendar_Span_Reporting_Rate_Pct",
            "Peer_Benchmark_Reporting_Rate_Pct",
            "Adjusted_Gap_Pct_Points",
            "Adjusted_Reporting_Index_Pct",
            "Weekdays_Below_Peer_Benchmark",
            "Adjusted_Rank_Within_Commodity",
        ]
    ]
    .sort_values("Adjusted_Reporting_Index_Pct")
    .head(15)
    .to_string(index=False)
)

print("\nSaved:")
print(PAIR_OUTPUT)
print(SUMMARY_OUTPUT)
