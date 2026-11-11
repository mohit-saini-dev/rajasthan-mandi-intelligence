import pandas as pd

dim_date = pd.read_csv('data/processed/dim_date.csv')
dim_commodity = pd.read_csv('data/processed/dim_commodity.csv')
fact = pd.read_csv('data/processed/fact_market_arrivals.csv')

fact_date = fact.merge(dim_date, on='Date_Id')
fact_date['Parsed_Date'] = pd.to_datetime(fact_date['Date'])

key_crops = [
    'Bajra(Pearl Millet/Cumbu)',
    'Mustard',
    'Bengal Gram(Gram)(Whole)',
    'Wheat',
    'Barley(Jau)'
]

target_commodities = dim_commodity[
    dim_commodity['Commodity_Name'].isin(key_crops)
]

fact_filtered = fact_date[
    fact_date['Commodity_Id'].isin(target_commodities['Commodity_Id'])
].copy()

# One observation per market-commodity-date
pair_dates = fact_filtered[
    ['Market_Id', 'Commodity_Id', 'Parsed_Date']
].drop_duplicates()

# Retain pairs with at least 200 reported days
pair_counts = (
    pair_dates.groupby(['Market_Id', 'Commodity_Id'])
    .size()
    .reset_index(name='Reported_Days')
)

eligible_pairs = pair_counts[
    pair_counts['Reported_Days'] >= 200
][['Market_Id', 'Commodity_Id']]

pair_dates = pair_dates.merge(
    eligible_pairs,
    on=['Market_Id', 'Commodity_Id'],
    how='inner'
)

# Calculate weekday reporting rates using each pair's
# first-to-last observed date as its observation span.
pair_dates['Weekday'] = pair_dates['Parsed_Date'].dt.day_name()

weekday_order = [
    'Monday', 'Tuesday', 'Wednesday',
    'Thursday', 'Friday', 'Saturday', 'Sunday'
]

results = []

for (market_id, commodity_id), group in pair_dates.groupby(
    ['Market_Id', 'Commodity_Id']
):
    start = group['Parsed_Date'].min()
    end = group['Parsed_Date'].max()

    expected = pd.date_range(start, end, freq='D')
    expected_counts = expected.day_name().value_counts()

    observed_counts = group['Weekday'].value_counts()

    for weekday in weekday_order:
        expected_days = int(expected_counts.get(weekday, 0))
        reported_days = int(observed_counts.get(weekday, 0))

        results.append({
            'Market_Id': market_id,
            'Commodity_Id': commodity_id,
            'Weekday': weekday,
            'Reported_Days': reported_days,
            'Expected_Calendar_Weekdays': expected_days,
            'Reporting_Rate_Pct': (
                reported_days / expected_days * 100
                if expected_days else 0
            )
        })

weekday_report = pd.DataFrame(results)

summary = (
    weekday_report.groupby('Weekday')
    .agg(
        Total_Reported=('Reported_Days', 'sum'),
        Total_Expected=('Expected_Calendar_Weekdays', 'sum'),
        Mean_Pair_Reporting_Rate=('Reporting_Rate_Pct', 'mean'),
        Median_Pair_Reporting_Rate=('Reporting_Rate_Pct', 'median')
    )
    .reindex(weekday_order)
)

summary['Overall_Reporting_Rate_Pct'] = (
    summary['Total_Reported'] / summary['Total_Expected'] * 100
)

weekday_report.to_csv(
    'data/processed/weekday_reporting_by_pair.csv',
    index=False
)

summary.to_csv(
    'data/processed/weekday_reporting_summary.csv'
)

print('--- Normalized Weekday Reporting Summary ---')
print(summary.round(2))

print('\nEligible market-commodity pairs:', len(eligible_pairs))
print('Saved detailed and summary weekday reports.')
