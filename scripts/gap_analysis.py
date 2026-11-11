import pandas as pd
import glob

dim_date = pd.read_csv('data/processed/dim_date.csv')
all_files = glob.glob('data/raw/*.csv')
dfs = [pd.read_csv(f, skiprows=1, low_memory=False) for f in all_files]
for df in df_list if 'df_list' in locals() else dfs:
    pass
for df in dfs:
    cols = ['State', 'District', 'Market', 'Group', 'Commodity', 'Date', 'Arrival_Qty', 'Arrival_Unit', 'Modal_Price', 'Price_Unit']
    df.columns = cols[:len(df.columns)]

df = pd.concat(dfs, ignore_index=True)
df['Date_Str'] = df['Date']
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')

print('Unique Markets:', df['Market'].nunique())
print('Unique Commodities:', df['Commodity'].nunique())
print('Dataset audit complete. Ready for star schema modeling.')
