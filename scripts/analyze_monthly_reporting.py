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

# Retain pairs with at least 200 reported days (matching our eligible pool)
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

# Extract Year and Month Name
pair_dates['Year'] = pair_dates['Parsed_Date'].dt.year
pair_dates['Month'] = pair_dates['Parsed_Date'].dt.month_name()
pair_dates['Month_Num'] = pair_dates['Parsed_Date'].dt.month

# Merge commodity name for readability
pair_dates = pair_dates.merge(target_commodities[['Commodity_Id', 'Commodity_Name']], on='Commodity_Id')

# Aggregate reporting counts by Commodity, Year, and Month
monthly_summary = (
    pair_dates.groupby(['Commodity_Name', 'Year', 'Month_Num', 'Month'])
    .agg(
        Active_Pairs_Reporting=('Market_Id', 'nunique'),
        Total_Reported_Records=('Parsed_Date', 'count')
    )
    .reset_index()
    .sort_values(['Commodity_Name', 'Year', 'Month_Num'])
)

# Flag incomplete months (specifically November 2026)
monthly_summary['Is_Incomplete_Month'] = monthly_summary.apply(
    lambda row: True if row['Year'] == 2026 and row['Month'] == 'November' else False, axis=1
)

output_cols = ['Commodity_Name', 'Year', 'Month', 'Active_Pairs_Reporting', 'Total_Reported_Records', 'Is_Incomplete_Month']
monthly_summary = monthly_summary[output_cols]

monthly_summary.to_csv('data/processed/monthly_reporting_by_commodity_year.csv', index=False)

print('--- Monthly Reporting Summary Preview ---')
print(monthly_summary.head(15).to_string(index=False))
print('\nSaved monthly reporting analysis to data/processed/monthly_reporting_by_commodity_year.csv')
