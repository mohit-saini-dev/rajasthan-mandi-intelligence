import calendar
import pandas as pd

# Load existing dimensional and fact tables
dim_date = pd.read_csv("data/processed/dim_date.csv")
dim_commodity = pd.read_csv("data/processed/dim_commodity.csv")
fact = pd.read_csv("data/processed/fact_market_arrivals.csv")

# Attach calendar dates to fact observations
fact_date = fact.merge(dim_date, on="Date_Id", how="inner")
fact_date["Parsed_Date"] = pd.to_datetime(fact_date["Date"], errors="coerce")
fact_date = fact_date.dropna(subset=["Parsed_Date"])

# Five selected crops
key_crops = [
    "Bajra(Pearl Millet/Cumbu)",
    "Mustard",
    "Bengal Gram(Gram)(Whole)",
    "Wheat",
    "Barley(Jau)"
]

target_commodities = dim_commodity[
    dim_commodity["Commodity_Name"].isin(key_crops)
][["Commodity_Id", "Commodity_Name"]]

fact_filtered = fact_date[
    fact_date["Commodity_Id"].isin(target_commodities["Commodity_Id"])
].copy()

# One observation per market-commodity-date
pair_dates = fact_filtered[
    ["Market_Id", "Commodity_Id", "Parsed_Date"]
].drop_duplicates()

# Keep the same eligible population: at least 200 reported days
pair_stats = (
    pair_dates.groupby(["Market_Id", "Commodity_Id"])
    .agg(
        Reported_Days=("Parsed_Date", "nunique"),
        First_Reported_Date=("Parsed_Date", "min"),
        Last_Reported_Date=("Parsed_Date", "max")
    )
    .reset_index()
)

eligible_pairs = pair_stats[
    pair_stats["Reported_Days"] >= 200
].merge(
    target_commodities,
    on="Commodity_Id",
    how="left"
)

eligible_dates = pair_dates.merge(
    eligible_pairs[["Market_Id", "Commodity_Id"]],
    on=["Market_Id", "Commodity_Id"],
    how="inner"
)

# Overall observation window, derived from the available data
data_start = eligible_dates["Parsed_Date"].min()
data_end = eligible_dates["Parsed_Date"].max()

# Count distinct reporting days for each pair and month
eligible_dates["Year"] = eligible_dates["Parsed_Date"].dt.year
eligible_dates["Month_Num"] = eligible_dates["Parsed_Date"].dt.month

pair_month_counts = (
    eligible_dates.groupby(
        ["Market_Id", "Commodity_Id", "Year", "Month_Num"]
    )["Parsed_Date"]
    .nunique()
)

reported_lookup = pair_month_counts.to_dict()

# Build a complete pair-month panel within each pair's observed date range
panel_rows = []

for pair in eligible_pairs.itertuples(index=False):
    first_date = pair.First_Reported_Date
    last_date = pair.Last_Reported_Date

    first_month = first_date.to_period("M")
    last_month = last_date.to_period("M")

    for month in pd.period_range(first_month, last_month, freq="M"):
        month_start = month.start_time
        month_end = month.end_time.normalize()

        expected_start = max(first_date, month_start, data_start)
        expected_end = min(last_date, month_end, data_end)

        expected_days = (expected_end - expected_start).days + 1

        if expected_days <= 0:
            continue

        reported_days = reported_lookup.get(
            (pair.Market_Id, pair.Commodity_Id, month.year, month.month),
            0
        )

        panel_rows.append({
            "Market_Id": pair.Market_Id,
            "Commodity_Id": pair.Commodity_Id,
            "Commodity_Name": pair.Commodity_Name,
            "Year": month.year,
            "Month_Num": month.month,
            "Month": calendar.month_name[month.month],
            "Expected_Pair_Days": expected_days,
            "Reported_Pair_Days": reported_days
        })

pair_month_panel = pd.DataFrame(panel_rows)

# Aggregate to crop-year-month level
monthly_rates = (
    pair_month_panel.groupby(
        ["Commodity_Name", "Year", "Month_Num", "Month"]
    )
    .agg(
        Eligible_Pairs_In_Span=("Market_Id", "size"),
        Pairs_Reporting=(
            "Reported_Pair_Days",
            lambda values: int((values > 0).sum())
        ),
        Expected_Pair_Days=("Expected_Pair_Days", "sum"),
        Reported_Pair_Days=("Reported_Pair_Days", "sum")
    )
    .reset_index()
    .sort_values(["Commodity_Name", "Year", "Month_Num"])
)

monthly_rates["Calendar_Span_Reporting_Rate_Pct"] = (
    monthly_rates["Reported_Pair_Days"]
    / monthly_rates["Expected_Pair_Days"]
    * 100
).round(2)

# Flag months that are only partially covered by the overall data window
monthly_rates["Is_Incomplete_Month"] = monthly_rates["Month_Num"].apply(
    lambda month_num: False
)

monthly_rates["Is_Incomplete_Month"] = monthly_rates.apply(
    lambda row: (
        pd.Period(
            f"{int(row['Year'])}-{int(row['Month_Num']):02d}",
            freq="M"
        ).start_time < data_start
        or
        pd.Period(
            f"{int(row['Year'])}-{int(row['Month_Num']):02d}",
            freq="M"
        ).end_time.normalize() > data_end
    ),
    axis=1
)

# Save detailed pair-month panel and aggregated monthly rates
pair_month_panel.to_csv(
    "data/processed/monthly_reporting_pair_month_panel.csv",
    index=False
)

monthly_rates.to_csv(
    "data/processed/monthly_reporting_rates_by_commodity_year.csv",
    index=False
)

print("Eligible market-commodity pairs:", len(eligible_pairs))
print("Observation window:", data_start.date(), "to", data_end.date())
print("Pair-month panel rows:", len(pair_month_panel))

print("\n--- Normalized Monthly Reporting Rates ---")
print(monthly_rates.head(20).to_string(index=False))

print("\nSaved:")
print("data/processed/monthly_reporting_pair_month_panel.csv")
print("data/processed/monthly_reporting_rates_by_commodity_year.csv")
