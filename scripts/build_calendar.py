import pandas as pd
import glob
import os

os.makedirs('data/processed', exist_ok=True)

# 1. Build Master Calendar (dim_date)
date_range = pd.date_range(start='2023-01-01', end='2026-12-31', freq='D')
dim_date = pd.DataFrame({'Date': date_range})
dim_date['Date_Id'] = dim_date['Date'].dt.strftime('%Y%m%d').astype(int)
dim_date['Year'] = dim_date['Date'].dt.year
dim_date['Quarter'] = 'Q' + dim_date['Date'].dt.quarter.astype(str)
dim_date['Month_No'] = dim_date['Date'].dt.month
dim_date['Month_Name'] = dim_date['Date'].dt.strftime('%B')
dim_date['Day_Name'] = dim_date['Date'].dt.strftime('%A')
dim_date['Is_Weekend'] = dim_date['Day_Name'].isin(['Saturday', 'Sunday'])

dim_date.to_csv('data/processed/dim_date.csv', index=False)
print('Master calendar created:', len(dim_date), 'days saved to data/processed/dim_date.csv')

# 2. Audit Raw Mandi Files
all_files = glob.glob('data/raw/*.csv')
dfs = [pd.read_csv(f, skiprows=1, low_memory=False) for f in all_files]
for df in dfs:
    cols = ['State', 'District', 'Market', 'Group', 'Commodity', 'Date', 'Arrival_Qty', 'Arrival_Unit', 'Modal_Price', 'Price_Unit']
    df.columns = cols[:len(df.columns)]

combined_df = pd.concat(dfs, ignore_index=True)
combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%d-%m-%Y', errors='coerce')
print('Total raw records loaded:', f"{len(combined_df):,}")
min_d = combined_df['Date'].min().strftime('%Y-%m-%d')
max_d = combined_df['Date'].max().strftime('%Y-%m-%d')
print('Timeline coverage:', min_d, 'to', max_d)
