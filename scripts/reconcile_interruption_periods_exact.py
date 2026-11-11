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

    required = ["District", "Market", "Commodity", "Date"]
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
    ]

    processed_part = processed[
        processed["Market_Key"].eq(key)
        & processed["Date"].between(start, end)
    ]

    results.append({
        "Market": market,
        "Start": start.date(),
        "End": end.date(),
        "Raw_Rows": len(raw_part),
        "Raw_Distinct_Dates": raw_part["Date"].nunique(),
        "Processed_Rows": len(processed_part),
        "Processed_Distinct_Dates": processed_part["Date"].nunique(),
        "Raw_Commodities": raw_part["Commodity"].nunique(),
        "Raw_First_Date": raw_part["Date"].min().date() if not raw_part.empty else None,
        "Raw_Last_Date": raw_part["Date"].max().date() if not raw_part.empty else None,
    })

    print(f"\n--- {market} ---")

    if raw_part.empty:
        print("No exact-label raw records in this period.")
    else:
        print(
            raw_part.groupby("Commodity")
            .agg(
                Raw_Rows=("Date", "size"),
                Distinct_Dates=("Date", "nunique"),
                First_Date=("Date", "min"),
                Last_Date=("Date", "max"),
            )
            .reset_index()
            .to_string(index=False)
        )

summary = pd.DataFrame(results)

summary.to_csv(
    "data/processed/exact_interruption_raw_reconciliation.csv",
    index=False,
)

print("\n--- RAW VS PROCESSED RECONCILIATION ---")
print(summary.to_string(index=False))

print("\nSaved: data/processed/exact_interruption_raw_reconciliation.csv")
