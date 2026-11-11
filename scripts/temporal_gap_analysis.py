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

obs_start = fact_filtered['Parsed_Date'].min()
obs_end = fact_filtered['Parsed_Date'].max()
obs_days = (obs_end - obs_start).days + 1
total_calendar_days = len(dim_date)

print(f'Observation Window: {obs_start.strftime("%Y-%m-%d")} to {obs_end.strftime("%Y-%m-%d")} ({obs_days} days)')

gap_summary = fact_filtered.groupby(['Market_Id', 'Commodity_Id']).agg(
    Reported_Days=('Date_Id', 'count'),
    First_Reported_Date=('Parsed_Date', 'min'),
    Last_Reported_Date=('Parsed_Date', 'max')
).reset_index()

gap_summary['Expected_Calendar_Days'] = total_calendar_days
gap_summary['Expected_Observation_Days'] = obs_days
gap_summary['Calendar_Coverage_Pct'] = (gap_summary['Reported_Days'] / total_calendar_days) * 100
gap_summary['Observation_Window_Coverage_Pct'] = (gap_summary['Reported_Days'] / obs_days) * 100

gap_summary = gap_summary.merge(dim_market, on='Market_Id').merge(dim_commodity, on='Commodity_Id')

col_order = ['Market_Id', 'Market_Name', 'Commodity_Id', 'Commodity_Name', 'Reported_Days', 'Expected_Calendar_Days', 'Calendar_Coverage_Pct', 'Observation_Window_Coverage_Pct', 'First_Reported_Date', 'Last_Reported_Date']
gap_summary = gap_summary[col_order]

gap_summary.to_csv('data/processed/temporal_gap_report_refined.csv', index=False)
print('Refined temporal gap report successfully saved to data/processed/temporal_gap_report_refined.csv')
