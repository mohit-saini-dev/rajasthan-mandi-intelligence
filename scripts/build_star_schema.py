import pandas as pd
import glob
import os

os.makedirs('data/processed', exist_ok=True)

# 1. Load Master Calendar and Raw Files
dim_date = pd.read_csv('data/processed/dim_date.csv')
all_files = glob.glob('data/raw/*.csv')
dfs = [pd.read_csv(f, skiprows=1, low_memory=False) for f in all_files]
for df in dfs:
    cols = ['State', 'District', 'Market', 'Group', 'Commodity', 'Date', 'Arrival_Qty', 'Arrival_Unit', 'Modal_Price', 'Price_Unit']
    df.columns = cols[:len(df.columns)]

df = pd.concat(dfs, ignore_index=True)
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
df.dropna(subset=['Date'], inplace=True)
df['Date_Id'] = df['Date'].dt.strftime('%Y%m%d').astype(int)

# 2. Build Dimension Tables
dim_market = pd.DataFrame({'Market_Name': df['Market'].dropna().unique()})
dim_market['Market_Id'] = range(1, len(dim_market) + 1)

dim_commodity = pd.DataFrame({'Commodity_Name': df['Commodity'].dropna().unique()})
dim_commodity['Commodity_Id'] = range(1, len(dim_commodity) + 1)

# Save Dimensions
dim_market.to_csv('data/processed/dim_market.csv', index=False)
dim_commodity.to_csv('data/processed/dim_commodity.csv', index=False)

# 3. Build Fact Table
fact_df = df.merge(dim_market, left_on='Market', right_on='Market_Name', how='left')
fact_df = fact_df.merge(dim_commodity, left_on='Commodity', right_on='Commodity_Name', how='left')

fact_table = fact_df[['Date_Id', 'Market_Id', 'Commodity_Id', 'Arrival_Qty', 'Modal_Price']].copy()
fact_table.dropna(subset=['Date_Id', 'Market_Id', 'Commodity_Id'], inplace=True)

fact_table.to_csv('data/processed/fact_market_arrivals.csv', index=False)
print('Star schema complete! Saved dim_market, dim_commodity, and fact_market_arrivals to data/processed/')
