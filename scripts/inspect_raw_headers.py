import pandas as pd
import glob

raw_files = glob.glob('data/raw/*.csv')
if raw_files:
    sample_file = raw_files[0]
    df = pd.read_csv(sample_file, nrows=5, low_memory=False)
    print(f"Sample file: {sample_file}")
    print("Columns found in raw export:")
    for col in df.columns:
        print(f" - {col}")
    print("\nFirst 3 rows of data:")
    print(df.head(3))
else:
    print("No raw files found.")
