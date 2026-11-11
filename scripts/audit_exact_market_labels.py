import pandas as pd
import glob

TARGETS = [
    "Osiyan Mathania APMC",
    "Barisadri APMC",
    "HanumangarhTown APMC",
    "Hanumangarh Town APMC",
    "Hanumangarh APMC",
    "Raniwara APMC",
    "Kotputli APMC",
]

frames = []

for file in sorted(glob.glob("data/raw/*.csv")):
    df = pd.read_csv(file, header=1, low_memory=False)

    required = ["District", "Market", "Commodity", "Date"]
    if not set(required).issubset(df.columns):
        print("Skipped:", file)
        continue

    part = df[required].copy()
    part["Date"] = pd.to_datetime(
        part["Date"], errors="coerce", dayfirst=True
    )
    part = part.dropna(subset=["Date"])
    frames.append(part)

raw = pd.concat(frames, ignore_index=True)

# Preserve internal spaces. Only trim outer whitespace and ignore case.
raw["Market_Exact_Key"] = (
    raw["Market"].astype(str).str.strip().str.casefold()
)

raw["District_Exact_Key"] = (
    raw["District"].astype(str).str.strip().str.casefold()
)

print("--- EXACT RAW MARKET LABEL SUMMARY ---")

for target in TARGETS:
    key = target.strip().casefold()
    subset = raw[raw["Market_Exact_Key"] == key]

    print(f"\nTARGET: {target}")
    if subset.empty:
        print("No exact raw label found.")
        continue

    summary = (
        subset.groupby(["District", "Market"])
        .agg(
            Raw_Rows=("Date", "size"),
            Distinct_Dates=("Date", "nunique"),
            First_Date=("Date", "min"),
            Last_Date=("Date", "max"),
            Commodities=("Commodity", "nunique"),
        )
        .reset_index()
    )

    print(summary.to_string(index=False))

print("\n--- HANUMANGARH LABELS: EXACT SEPARATION ---")

han = raw[
    raw["Market"].astype(str).str.contains(
        "Hanumangarh", case=False, na=False
    )
]

print(
    han.groupby(["District", "Market"])
    .agg(
        Raw_Rows=("Date", "size"),
        Distinct_Dates=("Date", "nunique"),
        First_Date=("Date", "min"),
        Last_Date=("Date", "max"),
    )
    .reset_index()
    .sort_values(["District", "Market"])
    .to_string(index=False)
)
