from pathlib import Path
import pandas as pd

fact_path = Path("data/processed/fact_market_arrivals.csv")
date_path = Path("data/processed/dim_date.csv")
market_path = Path("data/processed/dim_market.csv")
commodity_path = Path("data/processed/dim_commodity.csv")
consistency_path = Path("data/processed/market_reporting_consistency.csv")

monthly_output = Path(
    "data/processed/trailing_silence_monthly_diagnostic.csv"
)
summary_output = Path(
    "data/processed/trailing_silence_summary.csv"
)

required_files = [
    fact_path, date_path, market_path,
    commodity_path, consistency_path,
]
for path in required_files:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")

fact = pd.read_csv(fact_path)
dates = pd.read_csv(date_path)
markets = pd.read_csv(market_path)
commodities = pd.read_csv(commodity_path)
consistency = pd.read_csv(consistency_path)

dates["Date"] = pd.to_datetime(dates["Date"], errors="raise")

observations = (
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

crop_names = [
    "Bajra(Pearl Millet/Cumbu)",
    "Mustard",
    "Bengal Gram(Gram)(Whole)",
    "Wheat",
    "Barley(Jau)",
]

observations = observations[
    observations["Commodity_Name"].isin(crop_names)
].copy()

if observations.empty:
    raise ValueError("No observations found for the selected commodities.")

observations = observations.drop_duplicates(
    subset=["Market_Id", "Commodity_Id", "Date"]
)

cutoff = observations["Date"].max()
cutoff_month = cutoff.to_period("M")

pair_stats = (
    observations.groupby(
        ["Market_Id", "Commodity_Id", "Market_Name", "Commodity_Name"],
        as_index=False,
    )
    .agg(
        Reported_Days=("Date", "nunique"),
        First_Reported_Date=("Date", "min"),
        Last_Reported_Date=("Date", "max"),
    )
)

eligible_pairs = pair_stats[
    pair_stats["Reported_Days"] >= 200
].copy()

required_consistency = {
    "Market_Id", "Commodity_Id", "Adjusted_Reporting_Index_Pct"
}
missing = required_consistency - set(consistency.columns)
if missing:
    raise ValueError(
        f"Consistency file missing columns: {sorted(missing)}"
    )

selected = (
    consistency.sort_values(
        "Adjusted_Reporting_Index_Pct",
        ascending=True,
    )
    .drop_duplicates(["Market_Id", "Commodity_Id"])
    .head(15)
)

if len(selected) != 15:
    raise ValueError(f"Expected 15 selected pairs, found {len(selected)}.")

eligible_pairs["Pair_Key"] = list(zip(
    eligible_pairs["Market_Id"],
    eligible_pairs["Commodity_Id"],
))
selected["Pair_Key"] = list(zip(
    selected["Market_Id"],
    selected["Commodity_Id"],
))

selected = selected.drop(
    columns=["Market_Name", "Commodity_Name"],
    errors="ignore",
).merge(
    eligible_pairs[
        [
            "Pair_Key", "Market_Name", "Commodity_Name",
            "Reported_Days", "First_Reported_Date",
            "Last_Reported_Date",
        ]
    ],
    on="Pair_Key",
    how="left",
    validate="one_to_one",
)

if selected["Last_Reported_Date"].isna().any():
    raise ValueError(
        "Some selected pairs were not found in the eligible fact pairs."
    )

observations["Month"] = observations["Date"].dt.to_period("M")

monthly_active = (
    observations.groupby(
        ["Market_Id", "Commodity_Id", "Month"]
    )["Date"]
    .nunique()
    .rename("Reported_Days_In_Month")
    .reset_index()
)

monthly_active["Pair_Key"] = list(zip(
    monthly_active["Market_Id"],
    monthly_active["Commodity_Id"],
))

monthly_rows = []
summary_rows = []

for target in selected.to_dict("records"):
    pair_key = target["Pair_Key"]
    last_date = pd.Timestamp(target["Last_Reported_Date"])
    first_silent_month = last_date.to_period("M") + 1

    trailing_months = pd.period_range(
        first_silent_month,
        cutoff_month,
        freq="M",
    )

    target_monthly = []
    for month in trailing_months:
        month_start = month.start_time
        month_end = min(month.end_time.normalize(), cutoff)

        peers = eligible_pairs[
            (eligible_pairs["Commodity_Id"] == target["Commodity_Id"])
            & (eligible_pairs["Pair_Key"] != pair_key)
            & (eligible_pairs["First_Reported_Date"] <= month_end)
            & (eligible_pairs["Last_Reported_Date"] >= month_start)
        ]

        peer_keys = set(peers["Pair_Key"])
        peer_activity = monthly_active[
            (monthly_active["Month"] == month)
            & (monthly_active["Pair_Key"].isin(peer_keys))
        ]

        exposed_peers = len(peer_keys)
        active_peers = peer_activity["Pair_Key"].nunique()

        peer_rate = (
            active_peers / exposed_peers * 100
            if exposed_peers else float("nan")
        )

        row = {
            "Market_Id": target["Market_Id"],
            "Market_Name": target["Market_Name"],
            "Commodity_Id": target["Commodity_Id"],
            "Commodity_Name": target["Commodity_Name"],
            "Month": str(month),
            "Last_Reported_Date": last_date.date().isoformat(),
            "Dataset_Cutoff_Date": cutoff.date().isoformat(),
            "Trailing_Silent_Month": True,
            "Is_Cutoff_Month_Partial": month == cutoff_month,
            "Exposed_Peer_Pairs": exposed_peers,
            "Active_Peer_Pairs": active_peers,
            "Peer_Monthly_Activity_Rate_Pct": peer_rate,
            "Peer_Activity_At_Least_20_Pct": (
                bool(peer_rate >= 20)
                if pd.notna(peer_rate) else False
            ),
        }
        monthly_rows.append(row)
        target_monthly.append(row)

    complete_month_rows = [
        row for row in target_monthly
        if not row["Is_Cutoff_Month_Partial"]
    ]

    partial_month_rows = [
        row for row in target_monthly
        if row["Is_Cutoff_Month_Partial"]
    ]

    peer_active_full_months = sum(
        row["Peer_Activity_At_Least_20_Pct"]
        for row in complete_month_rows
    )

    peer_active_partial_months = sum(
        row["Peer_Activity_At_Least_20_Pct"]
        for row in partial_month_rows
    )

    longest_full_streak = 0
    current_full_streak = 0

    for row in complete_month_rows:
        if row["Peer_Activity_At_Least_20_Pct"]:
            current_full_streak += 1
            longest_full_streak = max(
                longest_full_streak,
                current_full_streak,
            )
        else:
            current_full_streak = 0

    silent_days = (cutoff - last_date).days

    summary_rows.append({
        "Market_Id": target["Market_Id"],
        "Market_Name": target["Market_Name"],
        "Commodity_Id": target["Commodity_Id"],
        "Commodity_Name": target["Commodity_Name"],
        "Adjusted_Reporting_Index_Pct": target[
            "Adjusted_Reporting_Index_Pct"
        ],
        "Last_Reported_Date": last_date.date().isoformat(),
        "Dataset_Cutoff_Date": cutoff.date().isoformat(),
        "Trailing_Silent_Days": silent_days,
        "Trailing_Silent_Full_Months": len(complete_month_rows),
        "Trailing_Silent_Partial_Months": len(partial_month_rows),
        "Peer_Active_Trailing_Full_Months": peer_active_full_months,
        "Peer_Active_Trailing_Partial_Months": peer_active_partial_months,
        "Longest_Consecutive_Peer_Active_Full_Silent_Months":
            longest_full_streak,
    })

monthly_result = pd.DataFrame(monthly_rows)
summary_result = pd.DataFrame(summary_rows)

monthly_output.parent.mkdir(parents=True, exist_ok=True)

monthly_result.to_csv(monthly_output, index=False)
summary_result.to_csv(summary_output, index=False)

print("Dataset cutoff:", cutoff.date())
print("Eligible market-commodity pairs:", len(eligible_pairs))
print("Selected low-reporting pairs:", len(selected))
print("Trailing monthly diagnostic rows:", len(monthly_result))

print("\n--- Corrected Trailing Silence Summary ---")
if not summary_result.empty:
    print(
        summary_result.sort_values(
            "Trailing_Silent_Days",
            ascending=False,
        )[
            [
                "Market_Name", "Commodity_Name", "Last_Reported_Date",
                "Trailing_Silent_Days", "Trailing_Silent_Full_Months",
                "Trailing_Silent_Partial_Months",
            ]
        ].to_string(index=False)
    )
else:
    print("No trailing silent months found.")

print("\nSaved:")
print(monthly_output)
print(summary_output)
