import pandas as pd
import glob
import re
from pathlib import Path

RAW_DIR = "data/raw"
FACT_PATH = "data/processed/fact_market_arrivals.csv"
DATE_PATH = "data/processed/dim_date.csv"
MARKET_PATH = "data/processed/dim_market.csv"

targets = [
    ("Osiyan Mathania APMC", "Jodhpur", "2023-02-01", "2024-06-30"),
    ("Barisadri APMC", "Chittorgarh", "2023-04-01", "2024-06-30"),
    ("HanumangarhTown APMC", "Hanumangarh", "2025-05-01", "2025-10-31"),
    ("HanumangarhTown APMC", "Hanumangarh", "2023-11-01", "2024-01-31"),
    ("Raniwara APMC", "Jalore", "2023-04-01", "2023-06-30"),
    ("Kotputli APMC", "Jaipur", "2024-08-01", "2024-09-30"),
]

def norm(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())

raw_frames = []

for file in sorted(glob.glob(f"{RAW_DIR}/*.csv")):
    df = pd.read_csv(file, header=1, low_memory=False)

    required = ["District", "Market", "Commodity", "Date"]
    if not set(required).issubset(df.columns):
        print("Skipped:", Path(file).name)
        continue

    df["Date"] = pd.to_datetime(
        df["Date"], errors="coerce", dayfirst=True
    )
    df["Source_File"] = Path(file).name
    raw_frames.append(
        df[required + ["Source_File"]].copy()
    )

if not raw_frames:
    raise ValueError("No readable raw export rows.")

raw = pd.concat(raw_frames, ignore_index=True)
raw = raw.dropna(subset=["Date"])

raw["District_Key"] = raw["District"].map(norm)
raw["Market_Key"] = raw["Market"].map(norm)

fact = pd.read_csv(FACT_PATH)
dates = pd.read_csv(DATE_PATH)
markets = pd.read_csv(MARKET_PATH)

dates["Date"] = pd.to_datetime(dates["Date"], errors="raise")

processed = (
    fact.merge(
        dates[["Date_Id", "Date"]],
        on="Date_Id",
        how="inner",
        validate="many_to_one",
    )
    .merge(
        markets[["Market_Id", "Market_Name"]],
        on="Market_Id",
        how="left",
        validate="many_to_one",
    )
)

processed["Market_Key"] = processed["Market_Name"].map(norm)

raw_results = []
district_results = []

for market, district, start, end in targets:
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    exact = raw[
        (raw["Market_Key"] == norm(market))
        & (raw["District_Key"] == norm(district))
        & raw["Date"].between(start, end)
    ]

    district_rows = raw[
        (raw["District_Key"] == norm(district))
        & raw["Date"].between(start, end)
    ]

    processed_exact = processed[
        (processed["Market_Key"] == norm(market))
        & processed["Date"].between(start, end)
    ]

    raw_results.append({
        "Market": market,
        "District": district,
        "Start": start.date(),
        "End": end.date(),
        "Raw_Rows": len(exact),
        "Raw_Distinct_Dates": exact["Date"].nunique(),
        "Processed_Rows": len(processed_exact),
        "Processed_Distinct_Dates": processed_exact["Date"].nunique(),
        "Raw_Commodities": exact["Commodity"].nunique(),
        "Other_District_Market_Labels":
            district_rows.loc[
                district_rows["Market_Key"] != norm(market),
                "Market"
            ].nunique(),
    })

    labels = (
        district_rows.groupby("Market")
        .agg(
            Raw_Rows=("Date", "size"),
            Distinct_Dates=("Date", "nunique"),
            First_Date=("Date", "min"),
            Last_Date=("Date", "max"),
        )
        .reset_index()
        .sort_values("Raw_Rows", ascending=False)
    )

    for row in labels.itertuples(index=False):
        district_results.append({
            "Target_Market": market,
            "District": district,
            "Start": start.date(),
            "End": end.date(),
            "Observed_Market_Label": row.Market,
            "Raw_Rows": row.Raw_Rows,
            "Distinct_Dates": row.Distinct_Dates,
            "First_Date": row.First_Date.date(),
            "Last_Date": row.Last_Date.date(),
        })

summary = pd.DataFrame(raw_results)
district_detail = pd.DataFrame(district_results)

summary.to_csv(
    "data/processed/six_market_period_raw_reconciliation.csv",
    index=False,
)
district_detail.to_csv(
    "data/processed/six_market_period_district_activity.csv",
    index=False,
)

print("--- Exact market reconciliation ---")
print(summary.to_string(index=False))

print("\n--- Other market labels active in the same districts ---")
print(district_detail.to_string(index=False))

print("\nSaved:")
print("data/processed/six_market_period_raw_reconciliation.csv")
print("data/processed/six_market_period_district_activity.csv")
