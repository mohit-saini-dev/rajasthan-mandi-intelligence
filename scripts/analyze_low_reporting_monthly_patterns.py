import pandas as pd

CONSISTENCY_PATH = "data/processed/market_reporting_consistency.csv"
PANEL_PATH = "data/processed/monthly_reporting_pair_month_panel.csv"

MONTHLY_OUTPUT = "data/processed/low_reporting_monthly_profile.csv"
YEARLY_OUTPUT = "data/processed/low_reporting_yearly_profile.csv"
SEASONAL_OUTPUT = "data/processed/low_reporting_seasonal_profile.csv"

TOP_N = 15

keys = ["Market_Id", "Commodity_Id"]

consistency = pd.read_csv(CONSISTENCY_PATH)
panel = pd.read_csv(PANEL_PATH)

required_panel_columns = [
    "Market_Id",
    "Commodity_Id",
    "Commodity_Name",
    "Year",
    "Month_Num",
    "Month",
    "Expected_Pair_Days",
    "Reported_Pair_Days",
]

missing = [
    col for col in required_panel_columns
    if col not in panel.columns
]

if missing:
    raise ValueError(f"Missing panel columns: {missing}")

# Select the 15 lowest adjusted reporting indices.
top_pairs = (
    consistency.sort_values("Adjusted_Reporting_Index_Pct")
    .head(TOP_N)
    .copy()
)

# Ensure consistent key types.
for df in [top_pairs, panel]:
    df["Market_Id"] = pd.to_numeric(
        df["Market_Id"], errors="raise"
    ).astype(int)

    df["Commodity_Id"] = pd.to_numeric(
        df["Commodity_Id"], errors="raise"
    ).astype(int)

panel_key = keys + ["Year", "Month_Num"]

if panel.duplicated(panel_key).any():
    raise ValueError("Duplicate pair-month records detected.")

if (panel["Expected_Pair_Days"] <= 0).any():
    raise ValueError("Non-positive expected pair-days detected.")

if (
    panel["Reported_Pair_Days"] < 0
).any():
    raise ValueError("Negative reported pair-days detected.")

if (
    panel["Reported_Pair_Days"] > panel["Expected_Pair_Days"]
).any():
    raise ValueError("Reported pair-days exceed expected pair-days.")

# Attach monthly history to the selected pairs.
monthly = top_pairs[
    keys + [
        "Market_Name",
        "Adjusted_Reporting_Index_Pct",
    ]
].merge(
    panel,
    on=keys,
    how="left",
    validate="one_to_many",
    indicator=True
)

matched_pairs = (
    monthly.loc[monthly["_merge"] == "both", keys]
    .drop_duplicates()
)

if len(matched_pairs) != len(top_pairs):
    unmatched = top_pairs.merge(
        matched_pairs,
        on=keys,
        how="left",
        indicator=True
    )

    unmatched = unmatched[unmatched["_merge"] == "left_only"]

    raise ValueError(
        "Some selected pairs are missing from the monthly panel:\n"
        + unmatched[
            ["Market_Name", "Commodity_Name"]
        ].to_string(index=False)
    )

monthly = monthly.drop(columns="_merge")

# November 2026 is partial: source data ends on November 3.
monthly["Is_Incomplete_Month"] = (
    (monthly["Year"] == 2026)
    & (monthly["Month_Num"] == 11)
)

monthly["Monthly_Reporting_Rate_Pct"] = (
    monthly["Reported_Pair_Days"]
    / monthly["Expected_Pair_Days"]
    * 100
)

# Complete months only for year and seasonal comparisons.
complete = monthly[
    ~monthly["Is_Incomplete_Month"]
].copy()

# Year-level reporting profile for each selected pair.
yearly = (
    complete.groupby(
        keys + ["Market_Name", "Commodity_Name", "Year"]
    )
    .agg(
        Months_Represented=("Month_Num", "nunique"),
        Expected_Pair_Days=("Expected_Pair_Days", "sum"),
        Reported_Pair_Days=("Reported_Pair_Days", "sum"),
        Zero_Reporting_Months=(
            "Reported_Pair_Days",
            lambda values: int((values == 0).sum())
        ),
    )
    .reset_index()
)

yearly["Yearly_Reporting_Rate_Pct"] = (
    yearly["Reported_Pair_Days"]
    / yearly["Expected_Pair_Days"]
    * 100
)

# Calendar-month seasonality across complete months and years.
seasonal = (
    complete.groupby(
        keys + ["Market_Name", "Commodity_Name", "Month_Num", "Month"]
    )
    .agg(
        Complete_Months_Represented=("Year", "nunique"),
        Expected_Pair_Days=("Expected_Pair_Days", "sum"),
        Reported_Pair_Days=("Reported_Pair_Days", "sum"),
        Zero_Reporting_Months=(
            "Reported_Pair_Days",
            lambda values: int((values == 0).sum())
        ),
    )
    .reset_index()
)

seasonal["Seasonal_Reporting_Rate_Pct"] = (
    seasonal["Reported_Pair_Days"]
    / seasonal["Expected_Pair_Days"]
    * 100
)

# Sort outputs.
monthly = monthly.sort_values(
    ["Commodity_Name", "Market_Name", "Year", "Month_Num"]
)

yearly = yearly.sort_values(
    ["Commodity_Name", "Market_Name", "Year"]
)

seasonal = seasonal.sort_values(
    ["Commodity_Name", "Market_Name", "Month_Num"]
)

# Save outputs.
monthly.to_csv(MONTHLY_OUTPUT, index=False)
yearly.to_csv(YEARLY_OUTPUT, index=False)
seasonal.to_csv(SEASONAL_OUTPUT, index=False)

print("Selected pairs:", len(top_pairs))
print("Monthly profile rows:", len(monthly))
print("Yearly profile rows:", len(yearly))
print("Seasonal profile rows:", len(seasonal))
print(
    "Partial November 2026 rows:",
    int(monthly["Is_Incomplete_Month"].sum())
)

print("\n--- Yearly reporting profile ---")
print(
    yearly[
        [
            "Commodity_Name",
            "Market_Name",
            "Year",
            "Months_Represented",
            "Yearly_Reporting_Rate_Pct",
            "Zero_Reporting_Months",
        ]
    ].to_string(index=False)
)

print("\n--- Seasonal reporting profile (%) ---")
seasonal_pivot = seasonal.pivot(
    index=["Commodity_Name", "Market_Name"],
    columns="Month_Num",
    values="Seasonal_Reporting_Rate_Pct"
)

print(seasonal_pivot.round(1).to_string())

print("\nSaved:")
print(MONTHLY_OUTPUT)
print(YEARLY_OUTPUT)
print(SEASONAL_OUTPUT)
