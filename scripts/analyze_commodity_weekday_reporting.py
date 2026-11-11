import pandas as pd

FACT_PATH = "data/processed/fact_market_arrivals.csv"
DATE_PATH = "data/processed/dim_date.csv"
COMMODITY_PATH = "data/processed/dim_commodity.csv"

PAIR_OUTPUT = "data/processed/commodity_weekday_reporting_by_pair.csv"
SUMMARY_OUTPUT = "data/processed/commodity_weekday_reporting_summary.csv"

TARGET_CROPS = [
    "Bajra(Pearl Millet/Cumbu)",
    "Mustard",
    "Bengal Gram(Gram)(Whole)",
    "Wheat",
    "Barley(Jau)",
]

MIN_REPORTED_DAYS = 200

WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

fact = pd.read_csv(FACT_PATH)
dates = pd.read_csv(DATE_PATH)
commodities = pd.read_csv(COMMODITY_PATH)

df = (
    fact.merge(dates[["Date_Id", "Date"]], on="Date_Id", how="left")
        .merge(
            commodities[["Commodity_Id", "Commodity_Name"]],
            on="Commodity_Id",
            how="left"
        )
)

df["Parsed_Date"] = pd.to_datetime(df["Date"], errors="coerce")

df = df[
    df["Commodity_Name"].isin(TARGET_CROPS)
].dropna(subset=["Parsed_Date"])

df = df.drop_duplicates(
    ["Market_Id", "Commodity_Id", "Parsed_Date"]
)

pair_stats = (
    df.groupby(
        ["Market_Id", "Commodity_Id", "Commodity_Name"]
    )
    .agg(
        Reported_Days=("Parsed_Date", "nunique"),
        First_Date=("Parsed_Date", "min"),
        Last_Date=("Parsed_Date", "max"),
    )
    .reset_index()
)

eligible_pairs = pair_stats[
    pair_stats["Reported_Days"] >= MIN_REPORTED_DAYS
].copy()

df = df.merge(
    eligible_pairs[
        ["Market_Id", "Commodity_Id", "Commodity_Name",
         "First_Date", "Last_Date"]
    ],
    on=["Market_Id", "Commodity_Id", "Commodity_Name"],
    how="inner"
)

df["Weekday"] = df["Parsed_Date"].dt.day_name()

reported = (
    df.groupby(
        ["Market_Id", "Commodity_Id", "Commodity_Name", "Weekday"]
    )
    .size()
    .rename("Total_Reported")
    .reset_index()
)

expected_rows = []

for row in eligible_pairs.itertuples(index=False):
    calendar = pd.date_range(
        start=row.First_Date,
        end=row.Last_Date,
        freq="D"
    )

    weekday_counts = pd.Series(
        calendar.day_name()
    ).value_counts()

    for weekday in WEEKDAYS:
        expected_rows.append({
            "Market_Id": row.Market_Id,
            "Commodity_Id": row.Commodity_Id,
            "Commodity_Name": row.Commodity_Name,
            "Weekday": weekday,
            "Total_Expected": int(weekday_counts.get(weekday, 0)),
        })

expected = pd.DataFrame(expected_rows)

pair_weekday = expected.merge(
    reported,
    on=["Market_Id", "Commodity_Id", "Commodity_Name", "Weekday"],
    how="left"
)

pair_weekday["Total_Reported"] = (
    pair_weekday["Total_Reported"].fillna(0).astype(int)
)

pair_weekday["Pair_Reporting_Rate_Pct"] = (
    pair_weekday["Total_Reported"]
    / pair_weekday["Total_Expected"]
    * 100
)

summary = (
    pair_weekday.groupby(
        ["Commodity_Name", "Weekday"]
    )
    .agg(
        Eligible_Pairs=("Market_Id", "nunique"),
        Total_Reported=("Total_Reported", "sum"),
        Total_Expected=("Total_Expected", "sum"),
        Mean_Pair_Reporting_Rate=(
            "Pair_Reporting_Rate_Pct", "mean"
        ),
        Median_Pair_Reporting_Rate=(
            "Pair_Reporting_Rate_Pct", "median"
        ),
    )
    .reset_index()
)

summary["Overall_Reporting_Rate_Pct"] = (
    summary["Total_Reported"]
    / summary["Total_Expected"]
    * 100
)

pair_weekday["Weekday"] = pd.Categorical(
    pair_weekday["Weekday"],
    categories=WEEKDAYS,
    ordered=True
)

summary["Weekday"] = pd.Categorical(
    summary["Weekday"],
    categories=WEEKDAYS,
    ordered=True
)

pair_weekday = pair_weekday.sort_values(
    ["Commodity_Name", "Weekday"]
)

summary = summary.sort_values(
    ["Commodity_Name", "Weekday"]
)

pair_weekday.to_csv(PAIR_OUTPUT, index=False)
summary.to_csv(SUMMARY_OUTPUT, index=False)

print("Eligible market-commodity pairs:", len(eligible_pairs))
print("Pair-weekday rows:", len(pair_weekday))
print("Summary rows:", len(summary))

print("\nCommodity-wise weekday reporting rates:")
print(
    summary[
        ["Commodity_Name", "Weekday",
         "Total_Reported", "Total_Expected",
         "Mean_Pair_Reporting_Rate",
         "Median_Pair_Reporting_Rate",
         "Overall_Reporting_Rate_Pct"]
    ].to_string(index=False)
)

print("\nSaved:")
print(PAIR_OUTPUT)
print(SUMMARY_OUTPUT)
