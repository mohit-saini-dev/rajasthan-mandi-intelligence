import pandas as pd
import glob

# 1. Verify Fact Table Grain Uniqueness (Point C)
fact = pd.read_csv('data/processed/fact_market_arrivals.csv')
total_rows = len(fact)
distinct_keys = fact[['Date_Id', 'Market_Id', 'Commodity_Id']].drop_duplicates().shape[0]
duplicate_count = total_rows - distinct_keys

print(f'Total Fact Rows: {total_rows}')
print(f'Distinct Composite Keys: {distinct_keys}')
print(f'Duplicate Count: {duplicate_count} (Expected: 0)')

# 2. Inspect the 24 Rejected Rows (Point A)
all_files = glob.glob('data/raw/*.csv')
dfs = [pd.read_csv(f, skiprows=1, low_memory=False) for f in all_files]
for df in dfs:
    cols = ['State', 'District', 'Market', 'Group', 'Commodity', 'Date', 'Arrival_Qty', 'Arrival_Unit', 'Modal_Price', 'Price_Unit']
    df.columns = cols[:len(df.columns)]

raw_df = pd.concat(dfs, ignore_index=True)
raw_df['Parsed_Date'] = pd.to_datetime(raw_df['Date'], format='%d-%m-%Y', errors='coerce')
rejected_rows = raw_df[raw_df['Parsed_Date'].isna()]

print(f'\nTotal Rejected Rows due to Date Parsing: {len(rejected_rows)}')
if len(rejected_rows) > 0:
    print('Sample of rejected date strings:')
    print(rejected_rows['Date'].head(10).unique())
    rejected_rows.to_csv('data/processed/rejected_date_rows.csv', index=False)
    print('Saved all rejected rows to data/processed/rejected_date_rows.csv for inspection.')
