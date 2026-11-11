from pathlib import Path
import pandas as pd
import glob

diagnostic_path = Path(
    "data/processed/trailing_silence_monthly_diagnostic.csv"
)

if not diagnostic_path.exists():
    raise FileNotFoundError(diagnostic_path)

diagnostic = pd.read_csv(diagnostic_path)

required = {
    "Market_Id", "Market_Name", "Commodity_Id",
    "Commodity_Name", "Month",
}
missing = required - set(diagnostic.columns)

if missing:
    raise ValueError(f"Missing diagnostic columns: {sorted(missing)}")

diagnostic["Month"] = pd.PeriodIndex(
    diagnostic["Month"], freq="M"
)

# Read all downloaded raw exports.
raw_frames = []

for file in sorted(glob.glob("data/raw/*.csv")):
    df = pd.read_csv(file, header=1, low_memory=False)

    required_raw = {"Market", "Commodity", "Date"}
    if not required_raw.issubset(df.columns):
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

    raw_frames.append(part)

if not raw_frames:
    raise ValueError("No usable raw export files were found.")

raw = pd.concat(raw_frames, ignore_index=True)

# Read processed facts and dimensions.
fact = pd.read_csv("data/processed/fact_market_arrivals.csv")
dates = pd.read_csv("data/processed/dim_date.csv")
markets = pd.read_csv("data/processed/dim_market.csv")
commodities = pd.read_csv("data/processed/dim_commodity.csv")

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
        validate="many_to_one",
    )
    .merge(
        commodities[["Commodity_Id", "Commodity_Name"]],
        on="Commodity_Id",
        validate="many_to_one",
    )
)

processed["Market_Key"] = (
    processed["Market_Name"].astype(str).str.strip().str.casefold()
)
processed["Commodity_Key"] = (
    processed["Commodity_Name"].astype(str).str.strip().str.casefold()
)

results = []

for target in diagnostic.to_dict("records"):
    market_key = str(target["Market_Name"]).strip().casefold()
    commodity_key = str(target["Commodity_Name"]).strip().casefold()
    month = target["Month"]

    start = month.start_time
    end = month.end_time.normalize()

    raw_part = raw[
        raw["Market_Key"].eq(market_key)
        & raw["Commodity_Key"].eq(commodity_key)
        & raw["Date"].between(start, end)
    ]

    processed_part = processed[
        processed["Market_Id"].eq(target["Market_Id"])
        & processed["Commodity_Id"].eq(target["Commodity_Id"])
        & processed["Date"].between(start, end)
    ]

    raw_dates = raw_part["Date"].nunique()
    processed_dates = processed_part["Date"].nunique()

    results.append({
        "Market_Id": target["Market_Id"],
        "Market_Name": target["Market_Name"],
        "Commodity_Id": target["Commodity_Id"],
        "Commodity_Name": target["Commodity_Name"],
        "Month": str(month),
        "Raw_Rows": len(raw_part),
        "Raw_Active_Dates": raw_dates,
        "Processed_Rows": len(processed_part),
        "Processed_Active_Dates": processed_dates,
        "Active_Date_Counts_Match": raw_dates == processed_dates,
        "Raw_Source_Records_Present": raw_dates > 0,
        "Processed_Records_Present": processed_dates > 0,
    })

result = pd.DataFrame(results)

output_path = Path(
    "data/processed/trailing_silence_raw_processed_audit.csv"
)

result.to_csv(output_path, index=False)

print("Trailing pair-months audited:", len(result))
print(
    "Raw and processed active-date counts match:",
    int(result["Active_Date_Counts_Match"].sum()),
    "of",
    len(result),
)

print("\n--- Trailing silence reconciliation ---")
print(result.to_string(index=False))

print("\n--- Reconciliation exceptions ---")
exceptions = result[~result["Active_Date_Counts_Match"]]

if exceptions.empty:
    print("No active-date count mismatches.")
else:
    print(exceptions.to_string(index=False))

print("\nSaved:", output_path)
