import pandas as pd
import glob

targets = [
    ("Osiyan Mathania APMC", "2023-02-01", "2024-06-30"),
    ("Barisadri APMC", "2023-04-01", "2024-06-30"),
    ("HanumangarhTown APMC", "2025-05-01", "2025-10-31"),
    ("Kotputli APMC", "2025-09-01", "2026-04-30"),
]

frames = []

for file in sorted(glob.glob("data/raw/*.csv")):
    df = pd.read_csv(file, header=1, low_memory=False)

    required = ["Market", "Commodity", "Date"]
    if not set(required).issubset(df.columns):
        continue

    part = df[required].copy()
    part["Date"] = pd.to_datetime(
        part["Date"], errors="coerce", dayfirst=True
    )
    frames.append(part.dropna(subset=["Date"]))

raw = pd.concat(frames, ignore_index=True)

raw["Market_Key"] = (
    raw["Market"].astype(str).str.strip().str.casefold()
)

fact = pd.read_csv("data/processed/fact_market_arrivals.csv")
dates = pd.read_csv("data/processed/dim_date.csv")
markets = pd.read_csv("data/processed/dim_market.csv")

dates["Date"] = pd.to_datetime(dates["Date"], errors="raise")

processed = (
    fact.merge(
        dates[["Date_Id", "Date"]],
        on="Date_Id",
        validate="many_to_one",
    )
    .merge(
        markets[["Market_Id", "Market_Name"]],
        on="Market_Id",
        how="left",
        validate="many_to_one",
    )
)

processed["Market_Key"] = (
    processed["Market_Name"].astype(str).str.strip().str.casefold()
)

results = []

for market, start, end in targets:
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    key = market.strip().casefold()

    raw_part = raw[
        raw["Market_Key"].eq(key)
        & raw["Date"].between(start, end)
    ].copy()

    processed_part = processed[
        processed["Market_Key"].eq(key)
        & processed["Date"].between(start, end)
    ].copy()

    months = pd.period_range(start, end, freq="M")

    for month in months:
        month_start = month.start_time
        month_end = month.end_time.normalize()

        r = raw_part[raw_part["Date"].between(month_start, month_end)]
        p = processed_part[
            processed_part["Date"].between(month_start, month_end)
        ]

        results.append({
            "Market": market,
            "Month": str(month),
            "Raw_Rows": len(r),
            "Raw_Active_Dates": r["Date"].nunique(),
            "Raw_Commodity_Date_Pairs": r[
                ["Commodity", "Date"]
            ].drop_duplicates().shape[0],
            "Processed_Rows": len(p),
            "Processed_Active_Dates": p["Date"].nunique(),
        })

result = pd.DataFrame(results)

result.to_csv(
    "data/processed/interruption_monthly_raw_processed_audit.csv",
    index=False,
)

print(result.to_string(index=False))

print("\nSaved:")
print("data/processed/interruption_monthly_raw_processed_audit.csv")
