import pandas as pd
import glob
import re
from pathlib import Path

RAW_DIR = "data/raw"
DIM_MARKET_PATH = "data/processed/dim_market.csv"
DIM_COMMODITY_PATH = "data/processed/dim_commodity.csv"
FACT_PATH = "data/processed/fact_market_arrivals.csv"
DATE_PATH = "data/processed/dim_date.csv"

targets = [
    ("Osiyan Mathania", "2023-02-01", "2024-06-30"),
    ("Barisadri", "2023-04-01", "2024-06-30"),
    ("Hanumangarh", "2025-05-01", "2025-10-31"),
    ("Hanumangarh", "2023-11-01", "2024-01-31"),
    ("Raniwara", "2023-04-01", "2023-06-30"),
    ("Kotputli", "2024-08-01", "2024-09-30"),
]

def normalize(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())

raw_files = sorted(glob.glob(f"{RAW_DIR}/*.csv"))

dim_market = pd.read_csv(DIM_MARKET_PATH)
dim_commodity = pd.read_csv(DIM_COMMODITY_PATH)
fact = pd.read_csv(FACT_PATH)
dim_date = pd.read_csv(DATE_PATH)

print("Raw export files:", len(raw_files))
print("\nDimension columns:")
print("Market:", dim_market.columns.tolist())
print("Commodity:", dim_commodity.columns.tolist())

market_name_col = next(
    (c for c in dim_market.columns if "market" in c.lower() and "id" not in c.lower()),
    None
)

commodity_name_col = next(
    (c for c in dim_commodity.columns if "commodity" in c.lower() and "id" not in c.lower()),
    None
)

if not market_name_col or not commodity_name_col:
    raise ValueError("Could not identify market or commodity name columns.")

print("\n--- Processed market-name candidates ---")
for target, _, _ in targets:
    token = normalize(target)
    candidates = dim_market[
        dim_market[market_name_col].astype(str).map(
            lambda x: token in normalize(x) or normalize(x) in token
        )
    ]
    print(f"\n{target}:")
    print(candidates.to_string(index=False))

raw_frames = []

for file in raw_files:
    df = pd.read_csv(file, header=1, low_memory=False)

    market_col = next(
        (c for c in df.columns if str(c).strip().lower() == "market"),
        None
    )
    date_col = next(
        (c for c in df.columns if "date" in str(c).lower()),
        None
    )
    commodity_col = next(
        (c for c in df.columns if "commodity" in str(c).lower()),
        None
    )

    if not all([market_col, date_col, commodity_col]):
        print("\nSkipped file with unrecognized columns:", Path(file).name)
        print(df.columns.tolist())
        continue

    df["Parsed_Date"] = pd.to_datetime(
        df[date_col], errors="coerce", dayfirst=True
    )
    df["Source_File"] = Path(file).name
    df["Raw_Market_Name"] = df[market_col].astype(str).str.strip()
    df["Raw_Commodity_Name"] = df[commodity_col].astype(str).str.strip()

    raw_frames.append(
        df[
            [
                "Raw_Market_Name",
                "Raw_Commodity_Name",
                "Parsed_Date",
                "Source_File",
            ]
        ]
    )

if not raw_frames:
    raise ValueError("No raw exports could be parsed.")

raw = pd.concat(raw_frames, ignore_index=True)
raw = raw.dropna(subset=["Parsed_Date"])

print("\n--- Raw market-name candidates ---")

for target, _, _ in targets:
    token = normalize(target)
    names = (
        raw.loc[
            raw["Raw_Market_Name"].map(
                lambda x: token in normalize(x) or normalize(x) in token
            ),
            "Raw_Market_Name",
        ]
        .value_counts()
    )

    print(f"\n{target}:")
    print(names.head(30).to_string() if not names.empty else "No candidate names found.")

# Detailed raw records for Hanumangarh windows.
print("\n--- Raw Hanumangarh records by market and commodity ---")

hanumangarh = raw[
    raw["Raw_Market_Name"].map(
        lambda x: "hanumangarh" in normalize(x)
    )
].copy()

for target, start, end in targets:
    if target != "Hanumangarh":
        continue

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    window = hanumangarh[
        hanumangarh["Parsed_Date"].between(start, end)
    ]

    print(f"\nWindow: {start.date()} to {end.date()}")
    if window.empty:
        print("No raw rows.")
    else:
        print(
            window.groupby(
                ["Raw_Market_Name", "Raw_Commodity_Name"]
            )
            .agg(
                Raw_Rows=("Parsed_Date", "size"),
                Distinct_Dates=("Parsed_Date", "nunique"),
                First_Date=("Parsed_Date", "min"),
                Last_Date=("Parsed_Date", "max"),
            )
            .reset_index()
            .sort_values("Raw_Rows", ascending=False)
            .to_string(index=False)
        )

# Compare the same periods against processed facts.
dim_date["Date"] = pd.to_datetime(dim_date["Date"], errors="raise")

processed = (
    fact.merge(
        dim_date[["Date_Id", "Date"]],
        on="Date_Id",
        how="inner",
        validate="many_to_one",
    )
    .merge(
        dim_market[["Market_Id", market_name_col]],
        on="Market_Id",
        how="left",
        validate="many_to_one",
    )
    .merge(
        dim_commodity[["Commodity_Id", commodity_name_col]],
        on="Commodity_Id",
        how="left",
        validate="many_to_one",
    )
)

processed_han = processed[
    processed[market_name_col].astype(str).map(
        lambda x: "hanumangarh" in normalize(x)
    )
].copy()

print("\n--- Processed Hanumangarh market IDs ---")
print(
    dim_market[
        dim_market[market_name_col].astype(str).map(
            lambda x: "hanumangarh" in normalize(x)
        )
    ].to_string(index=False)
)

for target, start, end in targets:
    if target != "Hanumangarh":
        continue

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    window = processed_han[
        processed_han["Date"].between(start, end)
    ]

    print(f"\nProcessed window: {start.date()} to {end.date()}")
    if window.empty:
        print("No processed fact rows.")
    else:
        print(
            window.groupby(
                [market_name_col, commodity_name_col]
            )
            .agg(
                Fact_Rows=("Date", "size"),
                Distinct_Dates=("Date", "nunique"),
                First_Date=("Date", "min"),
                Last_Date=("Date", "max"),
            )
            .reset_index()
            .sort_values("Fact_Rows", ascending=False)
            .to_string(index=False)
        )

print("\nReconciliation inspection complete.")
