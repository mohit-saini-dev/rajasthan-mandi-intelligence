import pandas as pd
import glob

print('--- DATA VALIDATION & PROFILING AUDIT ---')

# 1. Load Processed Tables
dim_date = pd.read_csv('data/processed/dim_date.csv')
dim_market = pd.read_csv('data/processed/dim_market.csv')
dim_commodity = pd.read_csv('data/processed/dim_commodity.csv')
fact = pd.read_csv('data/processed/fact_market_arrivals.csv')

# 2. Foreign Key & Orphan Check
orphan_dates = fact[~fact['Date_Id'].isin(dim_date['Date_Id'])]
orphan_markets = fact[~fact['Market_Id'].isin(dim_market['Market_Id'])]
orphan_commodities = fact[~fact['Commodity_Id'].isin(dim_commodity['Commodity_Id'])]

print(f'Orphan Date_Id records: {len(orphan_dates)}')
print(f'Orphan Market_Id records: {len(orphan_markets)}')
print(f'Orphan Commodity_Id records: {len(orphan_commodities)}')

# 3. Value Range & Outlier Profiling
print('\n--- Metric Summary & Profiling ---')
print(fact[['Arrival_Qty', 'Modal_Price']].describe())

# 4. Check for negative or zero anomalous values
negative_prices = (fact['Modal_Price'] < 0).sum()
zero_prices = (fact['Modal_Price'] == 0).sum()
negative_arrivals = (fact['Arrival_Qty'] < 0).sum()

print(f'Negative Prices: {negative_prices}')
print(f'Zero Prices: {zero_prices}')
print(f'Negative Arrivals: {negative_arrivals}')

print('\nValidation audit completed successfully.')
