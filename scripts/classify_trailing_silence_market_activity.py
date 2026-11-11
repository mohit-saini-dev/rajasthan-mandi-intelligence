from pathlib import Path
import pandas as pd
import glob

diagnostic_path = Path(
    "data/processed/trailing_silence_monthly_diagnostic.csv"
)
fact_path = Path("data/processed/fact_market_arrivals.csv")
date_path = Path("data/processed/dim_date.csv")

diagnostic = pd.read_csv(diagnostic_path)
fact = pd.read_csv(fact_path)
dates = pd.read_csv(date_path)

dates["Date"] = pd.to_datetime(dates["Date"], errors="raise")

cutoff = dates.merge(
    fact[["Date_Id"]].drop_duplicates(),
    on="Date_Id",
    validate="one_to_one",
)["Date"].max()

# Read all raw exports, retaining exact market and commodity labels.
frames = []

for file in sorted(glob.glob("data/raw/*.csv")):
    df = pd.read_csv(file, header=1, low_memory=False)

    required = {"Market", "Commodity", "Date"}
    if not required.issubset(df.columns):
        continue

    part = df[["Market", "Commodity", "Date"]].copy()
    part["Date"] = pd.to_datetime(
        part["Date"], errors="coerce", dayfirst=True
    )
    part = part.dropna(subset=["Date"])

    part["Market_Key"] = (
        part["Market"].astype(str).str.strip().str.casefold()
    )
    part["Commodity_Key"] = (
        part["Commodity"].astype(str).str.strip().str.casefold()
    )

    frames.append(part)

if not frames:
    raise ValueError("No usable raw export files found.")

raw = pd.concat(frames, ignore_index=True)

results = []

for target in diagnostic.to_dict("records"):
    month = pd.Period(target["Month"], freq="M")
    start = month.start_time
    end = min(month.end_time.normalize(), cutoff)

    market_key = str(target["Market_Name"]).strip().casefold()
    commodity_key = str(target["Commodity_Name"]).strip().casefold()

    market_month = raw[
        raw["Market_Key"].eq(market_key)
        & raw["Date"].between(start, end)
    ]

    target_month = market_month[
        market_month["Commodity_Key"].eq(commodity_key)
    ]

    active_commodities = sorted(
        market_month["Commodity"].dropna().astype(str).unique().tolist()
    )

    if market_month.empty:
        classification = "Potentially market-wide source silence"
    else:
        classification = "Commodity-specific source silence"

    results.append({
        "Market_Id": target["Market_Id"],
        "Market_Name": target["Market_Name"],
        "Commodity_Id": target["Commodity_Id"],
        "Commodity_Name": target["Commodity_Name"],
        "Month": str(month),
        "Audit_End_Date": end.date().isoformat(),
        "Market_Raw_Rows_All_Commodities": len(market_month),
        "Market_Active_Dates_All_Commodities": (
            market_month["Date"].nunique()
        ),
        "Other_Active_Commodity_Count": len(
            set(active_commodities) - {target["Commodity_Name"]}
        ),
        "Active_Commodities": "; ".join(active_commodities),
        "Target_Commodity_Raw_Rows": len(target_month),
        "Target_Commodity_Active_Dates": target_month["Date"].nunique(),
        "Classification": classification,
    })

result = pd.DataFrame(results)

output_path = Path(
    "data/processed/trailing_silence_market_wide_audit.csv"
)
output_path.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(output_path, index=False)

print("Dataset cutoff:", cutoff.date())
print("Pair-months audited:", len(result))

print("\n--- Classification summary ---")
print(result["Classification"].value_counts().to_string())

print("\n--- Market-wide trailing silence audit ---")
print(result.to_string(index=False))

print("\nSaved:", output_path)
