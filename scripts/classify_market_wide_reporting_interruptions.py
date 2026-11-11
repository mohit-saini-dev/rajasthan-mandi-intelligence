import pandas as pd

EVENTS_PATH = "data/processed/zero_reporting_interruption_events.csv"
FACT_PATH = "data/processed/fact_market_arrivals.csv"
DATE_PATH = "data/processed/dim_date.csv"

MONTHLY_OUTPUT = "data/processed/interruption_market_activity_by_month.csv"
SUMMARY_OUTPUT = "data/processed/interruption_market_activity_summary.csv"

keys = ["Market_Id", "Commodity_Id"]

events = pd.read_csv(EVENTS_PATH)
fact = pd.read_csv(FACT_PATH)
dim_date = pd.read_csv(DATE_PATH)

required_events = keys + [
    "Market_Name",
    "Commodity_Name",
    "Interruption_Start_Month",
    "Interruption_End_Month",
    "Consecutive_Zero_Months",
]

required_fact = keys + ["Date_Id"]
required_dates = ["Date_Id", "Date"]

for name, df, required in [
    ("events", events, required_events),
    ("fact", fact, required_fact),
    ("date dimension", dim_date, required_dates),
]:
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(
            f"{name} is missing required columns: {missing}"
        )

for df in [events, fact]:
    for col in keys:
        df[col] = pd.to_numeric(
            df[col], errors="raise"
        ).astype(int)

dim_date["Date"] = pd.to_datetime(
    dim_date["Date"], errors="raise"
)

if dim_date["Date_Id"].duplicated().any():
    raise ValueError("Duplicate Date_Id values in date dimension.")

if events.empty:
    raise ValueError("No interruption events found.")

events["Event_ID"] = range(1, len(events) + 1)

events["Start_Period"] = pd.PeriodIndex(
    events["Interruption_Start_Month"], freq="M"
)

events["End_Period"] = pd.PeriodIndex(
    events["Interruption_End_Month"], freq="M"
)

event_month_rows = []

for row in events.itertuples(index=False):
    periods = pd.period_range(
        row.Start_Period,
        row.End_Period,
        freq="M"
    )

    for period in periods:
        event_month_rows.append({
            "Event_ID": row.Event_ID,
            "Market_Id": row.Market_Id,
            "Commodity_Id": row.Commodity_Id,
            "Market_Name": row.Market_Name,
            "Commodity_Name": row.Commodity_Name,
            "Year": period.year,
            "Month_Num": period.month,
            "Month": str(period),
        })

event_months = pd.DataFrame(event_month_rows)

if event_months.empty:
    raise ValueError("No event-month rows generated.")

observations = fact.merge(
    dim_date[["Date_Id", "Date"]],
    on="Date_Id",
    how="inner",
    validate="many_to_one"
)

observations["Year"] = observations["Date"].dt.year
observations["Month_Num"] = observations["Date"].dt.month

market_month = (
    observations.groupby(
        ["Market_Id", "Year", "Month_Num"]
    )
    .agg(
        Market_Fact_Rows=("Date", "size"),
        Market_Observed_Days=("Date", "nunique"),
        Market_Active_Commodity_Count=("Commodity_Id", "nunique"),
    )
    .reset_index()
)

target_month = (
    observations.groupby(
        ["Market_Id", "Commodity_Id", "Year", "Month_Num"]
    )
    .agg(
        Target_Fact_Rows=("Date", "size"),
        Target_Observed_Days=("Date", "nunique"),
    )
    .reset_index()
)

event_observations = observations.merge(
    event_months[
        ["Event_ID", "Market_Id", "Commodity_Id", "Year", "Month_Num"]
    ],
    on=["Market_Id", "Year", "Month_Num"],
    how="inner",
    suffixes=("", "_Target")
)

event_other = event_observations[
    event_observations["Commodity_Id"]
    != event_observations["Commodity_Id_Target"]
].copy()

other_month = (
    event_other.groupby(
        ["Event_ID", "Market_Id", "Commodity_Id_Target",
         "Year", "Month_Num"]
    )
    .agg(
        Other_Commodity_Fact_Rows=("Date", "size"),
        Other_Commodity_Observed_Days=("Date", "nunique"),
        Other_Active_Commodity_Count=("Commodity_Id", "nunique"),
    )
    .reset_index()
    .rename(columns={"Commodity_Id_Target": "Commodity_Id"})
)

monthly = event_months.merge(
    market_month,
    on=["Market_Id", "Year", "Month_Num"],
    how="left",
    validate="many_to_one"
)

monthly = monthly.merge(
    target_month,
    on=keys + ["Year", "Month_Num"],
    how="left",
    validate="many_to_one"
)

monthly = monthly.merge(
    other_month,
    on=["Event_ID"] + keys + ["Year", "Month_Num"],
    how="left",
    validate="one_to_one"
)

count_columns = [
    "Market_Fact_Rows",
    "Market_Observed_Days",
    "Market_Active_Commodity_Count",
    "Target_Fact_Rows",
    "Target_Observed_Days",
    "Other_Commodity_Fact_Rows",
    "Other_Commodity_Observed_Days",
    "Other_Active_Commodity_Count",
]

monthly[count_columns] = monthly[count_columns].fillna(0).astype(int)

monthly["Market_Active"] = (
    monthly["Market_Observed_Days"] > 0
)

monthly["Other_Commodity_Active"] = (
    monthly["Other_Commodity_Observed_Days"] > 0
)

monthly["Target_Commodity_Active"] = (
    monthly["Target_Observed_Days"] > 0
)

summary_rows = []

for event_id, group in monthly.groupby("Event_ID"):
    group = group.sort_values(["Year", "Month_Num"])

    event = events.loc[
        events["Event_ID"] == event_id
    ].iloc[0]

    total_months = len(group)
    market_active_months = int(group["Market_Active"].sum())
    market_inactive_months = total_months - market_active_months

    if market_active_months == 0:
        classification = "Potentially market-wide"
    elif market_active_months == total_months:
        classification = "Commodity-specific"
    else:
        classification = "Mixed market activity"

    summary_rows.append({
        "Event_ID": event_id,
        "Market_Id": event["Market_Id"],
        "Market_Name": event["Market_Name"],
        "Commodity_Id": event["Commodity_Id"],
        "Commodity_Name": event["Commodity_Name"],
        "Interruption_Start_Month":
            event["Interruption_Start_Month"],
        "Interruption_End_Month":
            event["Interruption_End_Month"],
        "Interruption_Months": total_months,
        "Market_Active_Months": market_active_months,
        "Market_Inactive_Months": market_inactive_months,
        "Months_With_Other_Commodity_Activity":
            int(group["Other_Commodity_Active"].sum()),
        "Total_Other_Commodities_Observed":
            int(group["Other_Active_Commodity_Count"].sum()),
        "Classification": classification,
        "Monthly_Market_Activity": "; ".join(
            f"{row.Month}: "
            f"{row.Market_Active_Commodity_Count} commodities, "
            f"{row.Market_Observed_Days} observed days"
            for row in group.itertuples()
        ),
    })

summary = pd.DataFrame(summary_rows)

summary = summary.sort_values(
    ["Interruption_Months", "Market_Inactive_Months"],
    ascending=[False, False]
)

monthly = monthly.sort_values(
    ["Event_ID", "Year", "Month_Num"]
)

monthly.to_csv(MONTHLY_OUTPUT, index=False)
summary.to_csv(SUMMARY_OUTPUT, index=False)

print("Interruption events:", len(summary))
print("Event-month records:", len(monthly))

print("\n--- Classification counts ---")
print(
    summary["Classification"]
    .value_counts()
    .to_string()
)

print("\n--- Longest interruption classifications ---")
print(
    summary[
        [
            "Market_Name",
            "Commodity_Name",
            "Interruption_Start_Month",
            "Interruption_End_Month",
            "Interruption_Months",
            "Market_Active_Months",
            "Market_Inactive_Months",
            "Months_With_Other_Commodity_Activity",
            "Classification",
        ]
    ]
    .head(25)
    .to_string(index=False)
)

print("\n--- Potentially market-wide interruptions ---")
print(
    summary[
        summary["Classification"] == "Potentially market-wide"
    ][
        [
            "Market_Name",
            "Commodity_Name",
            "Interruption_Start_Month",
            "Interruption_End_Month",
            "Interruption_Months",
            "Classification",
        ]
    ].to_string(index=False)
)

print("\nSaved:")
print(MONTHLY_OUTPUT)
print(SUMMARY_OUTPUT)
