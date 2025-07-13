import pandas as pd
from config import IEA_CSV

def load_iea_data():
    df = pd.read_csv(IEA_CSV)
    # Handle both 'Country' and 'country'
    if 'Country' in df.columns:
        df = df.rename(columns={'Country': 'country'})
    if 'country' not in df.columns:
        raise ValueError("No 'country' or 'Country' column found in IEA CSV.")
    # Rename 'Time' to 'month' for clarity and consistency
    df = df.rename(columns={'Time': 'month'})
    # Convert 'month' to standard YYYY-MM format
    df['month'] = pd.to_datetime(df['month'], format='%y-%b').dt.to_period('M').astype(str)
    df = df[df['country'] == 'France']
    return df

if __name__ == "__main__":
    df = load_iea_data()
    print(df.head())
