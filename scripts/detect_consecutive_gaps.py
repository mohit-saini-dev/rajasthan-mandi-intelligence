import pandas as pd
import numpy as np

dim_date = pd.read_csv('data/processed/dim_date.csv')
dim_market = pd.read_csv('data/processed/dim_market.csv')
dim_commodity = pd.read_csv('data/processed/dim_commodity.csv')
fact = pd.read_csv('data/processed/fact_market_arrivals.csv')

fact_date = fact.merge(dim_date, on='Date_Id')
fact_date['Parsed_Date'] = pd.to_datetime(fact_date['Date'])

key_crops = ['Bajra(Pearl Millet/Cumbu)', 'Mustard', 'Bengal Gram(Gram)(Whole)', 'Wheat', 'Barley(Jau)']
target_commodities = dim_commodity[dim_commodity['Commodity_Name'].isin(key_crops)]
fact_filtered = fact_date[fact_date['Commodity_Id'].isin(target_commodities['Commodity_Id'])]

print('Calculating corrected maximum consecutive reporting gaps and gap date boundaries...')

results = []
for (market_id, commodity_id), group in fact_filtered.groupby(['Market_Id', 'Commodity_Id']):
    sorted_dates = group['Parsed_Date'].drop_duplicates().sort_values()
    date_diffs = sorted_dates.diff().dt.days - 1
    max_gap = date_diffs.max() if len(sorted_dates) > 1 else 0
    
    if pd.notna(max_gap) and max_gap > 0:
        # Exclude initial NaN and adjust index offset properly
        gap_position = int(date_diffs.iloc[1:].to_numpy().argmax()) + 1
        missing_start = sorted_dates.iloc[gap_position - 1] + pd.Timedelta(days=1)
        missing_end = sorted_dates.iloc[gap_position] - pd.Timedelta(days=1)
        previous_reported = sorted_dates.iloc[gap_position - 1]
        next_reported = sorted_dates.iloc[gap_position]
    else:
        missing_start = None
        missing_end = None
        previous_reported = None
        next_reported = None

    results.append({
        'Market_Id': market_id,
        'Commodity_Id': commodity_id,
        'Max_Consecutive_Missing_Days': max_gap if pd.notna(max_gap) else 0,
        'Gap_Previous_Reported_Date': previous_reported,
        'Gap_Next_Reported_Date': next_reported,
        'Max_Gap_Missing_Start_Date': missing_start,
        'Max_Gap_Missing_End_Date': missing_end
    })

gap_metrics = pd.DataFrame(results)

refined_report = pd.read_csv('data/processed/temporal_gap_report_refined.csv')

final_report = refined_report.merge(
    gap_metrics, 
    on=['Market_Id', 'Commodity_Id'], 
    how='left',
    validate='one_to_one'
)

final_report.to_csv('data/processed/temporal_gap_report_with_gaps.csv', index=False)
print('Successfully updated data/processed/temporal_gap_report_with_gaps.csv with corrected gap date boundaries.')
