import pandas as pd
import glob
import os

raw_files = glob.glob('data/raw/*.csv')
print(f'Found {len(raw_files)} raw export files to audit.')

# Define the targets to check
targets = [
    {'Market': 'Osiyan Mathania', 'Start': '2023-02-01', 'End': '2024-06-30'},
    {'Market': 'Barisadri', 'Start': '2023-04-01', 'End': '2024-06-30'},
    {'Market': 'Hanumangarh', 'Start': '2025-05-01', 'End': '2025-10-31'},
    {'Market': 'Hanumangarh', 'Start': '2023-11-01', 'End': '2024-01-31'},
    {'Market': 'Raniwara', 'Start': '2023-04-01', 'End': '2023-06-30'},
    {'Market': 'Kotputli', 'Start': '2024-08-01', 'End': '2024-09-30'}
]

found_records = []

for file in raw_files:
    try:
        df = pd.read_csv(file, low_memory=False)
        # Standard AGMARKNET columns usually include Market, Arrival_Date, Commodity, etc.
        # Let's inspect column names dynamically or search text matching
        market_cols = [c for c in df.columns if 'market' in c.lower()]
        date_cols = [c for c in df.columns if 'date' in c.lower() or 'arrival' in c.lower()]
        
        if not market_cols or not date_cols:
            continue
            
        m_col = market_cols[0]
        d_col = date_cols[0]
        
        df['Parsed_Date'] = pd.to_datetime(df[d_col], errors='coerce')
        
        for t in targets:
            match = df[df[m_col].astype(str).str.contains(t['Market'], case=False, na=False)]
            if not match.empty:
                filtered_date = match[(match['Parsed_Date'] >= t['Start']) & (match['Parsed_Date'] <= t['End'])]
                if not filtered_date.empty:
                    found_records.append({
                        'Target_Market': t['Market'],
                        'Expected_Window': f"{t['Start']} to {t['End']}",
                        'Raw_File': os.path.basename(file),
                        'Matching_Rows': len(filtered_date),
                        'Min_Date_Found': filtered_date['Parsed_Date'].min().strftime('%Y-%m-%d'),
                        'Max_Date_Found': filtered_date['Parsed_Date'].max().strftime('%Y-%m-%d')
                    })
    except Exception as e:
        print(f'Error reading {file}: {e}')

audit_df = pd.DataFrame(found_records)
if not audit_df.empty:
    print('\n--- Raw Export Audit Results ---')
    print(audit_df.to_string(index=False))
    audit_df.to_csv('data/processed/raw_export_audit_results.csv', index=False)
else:
    print('\nNo matching records found across raw files for the specified market-window targets. Investigating column structures...')
