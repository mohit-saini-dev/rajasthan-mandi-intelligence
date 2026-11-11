import pandas as pd

# Load processed tables
fact = pd.read_csv('data/processed/fact_market_arrivals.csv')
dim_market = pd.read_csv('data/processed/dim_market.csv')
dim_commodity = pd.read_csv('data/processed/dim_commodity.csv')
dim_date = pd.read_csv('data/processed/dim_date.csv')

# Merge to create analytical view
df = fact.merge(dim_market, on='Market_Id')
df = df.merge(dim_commodity, on='Commodity_Id')
df = df.merge(dim_date, left_on='Date_Id', right_on='Date_Id')

print('Total Fact Rows Joined:', len(df))
print('Sample Summary (Average Modal Price by Commodity):')
summary = df.groupby('Commodity_Name')['Modal_Price'].mean().reset_index()
print(summary.head(10))
