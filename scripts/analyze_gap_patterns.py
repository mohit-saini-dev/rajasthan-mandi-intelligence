import pandas as pd

dim_date = pd.read_csv('data/processed/dim_date.csv')
dim_market = pd.read_csv('data/processed/dim_market.csv')
dim_commodity = pd.read_csv('data/processed/dim_commodity.csv')
fact = pd.read_csv('data/processed/fact_market_arrivals.csv')

fact_date = fact.merge(dim_date, on='Date_Id')
fact_date['Parsed_Date'] = pd.to_datetime(fact_date['Date'])

key_crops = ['Bajra(Pearl Millet/Cumbu)', 'Mustard', 'Bengal Gram(Gram)(Whole)', 'Wheat', 'Barley(Jau)']
target_commodities = dim_commodity[dim_commodity['Commodity_Name'].isin(key_crops)]
fact_filtered = fact_date[fact_date['Commodity_Id'].isin(target_commodities['Commodity_Id'])]

# Analyze distribution of reported records across weekdays
fact_filtered['DayOfWeek'] = pd.to_datetime(fact_filtered['Date']).dt.day_name()
weekday_dist = fact_filtered['DayOfWeek'].value_counts()

print('--- Reported Records Distribution by Weekday ---')
print(weekday_dist)

# Analyze distribution across months
fact_filtered['Month'] = pd.to_datetime(fact_filtered['Date']).dt.month_name()
monthly_dist = fact_filtered['Month'].value_counts()

print('\n--- Reported Records Distribution by Month ---')
print(monthly_dist.head(12))
