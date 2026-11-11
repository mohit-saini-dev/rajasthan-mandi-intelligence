import pandas as pd

MONTHLY_PATH = "data/processed/zero_reporting_monthly_diagnostic.csv"
FACT_PATH = "data/processed/fact_market_arrivals.csv"
DATE_PATH = "data/processed/dim_date.csv"

OUTPUT_PATH = "data/processed/zero_reporting_interruption_events.csv"

keys = ["Market_Id", "Commodity_Id"]

monthly = pd.read_csv(MONTHLY_PATH)
fact = pd.read_csv(FACT_PATH)
dim_date = pd.read_csv(DATE_PATH)

# Validate required columns.
monthly_required = keys + [
    "Market_Name",
    "Commodity_Name",
    "Year",
    "Month_Num",
    "Reported_Pair_Days",
    "Expected_Pair_Days",
    "Peer_Monthly_Rate_Pct",
    "Peer_Active_Zero_Month",
]

fact_required = keys + ["Date_Id"]

date_required = ["Date_Id", "Date"]

for name, df, required in [
    ("monthly diagnostic", monthly, monthly_required),
    ("fact table", fact, fact_required),
    ("date dimension", dim_date, date_required),
]:
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(
            f"{name} is missing required columns: {missing}"
        )

# Normalize key and date fields.
for df in [monthly, fact]:
    for col in keys:
        df[col] = pd.to_numeric(
            df[col], errors="raise"
        ).astype(int)

dim_date["Date"] = pd.to_datetime(
    dim_date["Date"], errors="raise"
)

monthly["Year"] = pd.to_numeric(
    monthly["Year"], errors="raise"
).astype(int)

monthly["Month_Num"] = pd.to_numeric(
    monthly["Month_Num"], errors="raise"
).astype(int)

monthly["Month_Index"] = (
    monthly["Year"] * 12 + monthly["Month_Num"]
)

# Validate one row per pair-month.
panel_key = keys + ["Year", "Month_Num"]

if monthly.duplicated(panel_key).any():
    raise ValueError("Duplicate pair-month rows detected.")

# Get actual distinct observation dates for each selected pair.
observations = fact.merge(
    dim_date[["Date_Id", "Date"]],
    on="Date_Id",
    how="inner",
    validate="many_to_one"
)

observations = observations[
    observations[keys].apply(
        tuple, axis=1
    ).isin(
        set(monthly[keys].drop_duplicates().itertuples(
            index=False, name=None
        ))
    )
].copy()

observations = observations[
    keys + ["Date"]
].drop_duplicates()

observations = observations.sort_values(
    keys + ["Date"]
)

observed_dates = {
    pair: group["Date"].tolist()
    for pair, group in observations.groupby(keys)
}

# Identify consecutive zero-reporting runs for each pair.
events = []

for (market_id, commodity_id), group in monthly.groupby(keys):
    group = group.sort_values("Month_Index").reset_index(drop=True)

    market_name = group["Market_Name"].iloc[0]
    commodity_name = group["Commodity_Name"].iloc[0]

    pair_dates = observed_dates.get(
        (market_id, commodity_id), []
    )

    zero_positions = (
        group["Reported_Pair_Days"].eq(0).tolist()
    )

    position = 0

    while position < len(group):
        if not zero_positions[position]:
            position += 1
            continue

        # Find the end of this consecutive zero-reporting run.
        start_position = position

        while (
            position + 1 < len(group)
            and zero_positions[position + 1]
            and group.loc[position + 1, "Month_Index"]
                == group.loc[position, "Month_Index"] + 1
        ):
            position += 1

        end_position = position

        event_months = group.iloc[
            start_position:end_position + 1
        ].copy()

        start_month = pd.Timestamp(
            year=int(event_months.iloc[0]["Year"]),
            month=int(event_months.iloc[0]["Month_Num"]),
            day=1
        )

        end_month = pd.Timestamp(
            year=int(event_months.iloc[-1]["Year"]),
            month=int(event_months.iloc[-1]["Month_Num"]),
            day=1
        )

        end_month_last_day = (
            end_month + pd.offsets.MonthEnd(0)
        )

        # Find actual observations immediately surrounding the event.
        previous_dates = [
            date for date in pair_dates
            if date < start_month
        ]

        next_dates = [
            date for date in pair_dates
            if date > end_month_last_day
        ]

        previous_date = (
            max(previous_dates) if previous_dates else pd.NaT
        )

        next_date = (
            min(next_dates) if next_dates else pd.NaT
        )

        peer_active_count = int(
            event_months["Peer_Active_Zero_Month"].sum()
        )

        peer_rate_details = "; ".join(
            f"{int(row.Year)}-{int(row.Month_Num):02d}:"
            f"{row.Peer_Monthly_Rate_Pct:.1f}%"
            for row in event_months.itertuples()
        )

        event_length = len(event_months)

        events.append({
            "Market_Id": market_id,
            "Market_Name": market_name,
            "Commodity_Id": commodity_id,
            "Commodity_Name": commodity_name,
            "Interruption_Start_Month": start_month.strftime("%Y-%m"),
            "Interruption_End_Month": end_month.strftime("%Y-%m"),
            "Consecutive_Zero_Months": event_length,
            "Peer_Active_Zero_Months": peer_active_count,
            "All_Zero_Months_Peer_Active": (
                peer_active_count == event_length
            ),
            "Peer_Rates_By_Month": peer_rate_details,
            "Previous_Reported_Date": previous_date,
            "Next_Reported_Date": next_date,
            "Reporting_Resumed_After_Interruption": (
                pd.notna(next_date)
            ),
            "Days_Between_Surrounding_Reports": (
                (next_date - previous_date).days
                if pd.notna(previous_date)
                and pd.notna(next_date)
                else pd.NA
            ),
        })

        position += 1

events_df = pd.DataFrame(events)

if not events_df.empty:
    events_df = events_df.sort_values(
        [
            "Peer_Active_Zero_Months",
            "Consecutive_Zero_Months",
            "Market_Name",
            "Interruption_Start_Month",
        ],
        ascending=[False, False, True, True]
    )

events_df.to_csv(OUTPUT_PATH, index=False)

print("Selected market-commodity pairs:", len(monthly[keys].drop_duplicates()))
print("Interruption events:", len(events_df))

if not events_df.empty:
    print(
        "Events containing at least one peer-active zero month:",
        int((events_df["Peer_Active_Zero_Months"] > 0).sum())
    )

    print("\n--- Longest interruption events ---")
    print(
        events_df[
            [
                "Commodity_Name",
                "Market_Name",
                "Interruption_Start_Month",
                "Interruption_End_Month",
                "Consecutive_Zero_Months",
                "Peer_Active_Zero_Months",
                "Previous_Reported_Date",
                "Next_Reported_Date",
                "Reporting_Resumed_After_Interruption",
            ]
        ]
        .head(25)
        .to_string(index=False)
    )

    print("\n--- Events without a later observed report ---")
    print(
        events_df[
            events_df["Next_Reported_Date"].isna()
        ][
            [
                "Commodity_Name",
                "Market_Name",
                "Interruption_Start_Month",
                "Interruption_End_Month",
                "Consecutive_Zero_Months",
                "Previous_Reported_Date",
            ]
        ].to_string(index=False)
    )

print("\nSaved:")
print(OUTPUT_PATH)
