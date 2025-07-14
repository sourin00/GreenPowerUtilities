import pandas as pd
from config import COUNTRIES, MERGED_DATA_CSV, WEATHER_COLS

def clean_iea(df):
    # Standardize column names
    if 'Time' in df.columns:
        df = df.rename(columns={'Time': 'month'})
    if 'Country' in df.columns:
        df = df.rename(columns={'Country': 'country'})
    if 'Product' in df.columns:
        df = df.rename(columns={'Product': 'production_type'})
    if 'Value' in df.columns:
        df = df.rename(columns={'Value': 'value_gwh'})
    # Check for required columns
    required_cols = {'month', 'country', 'Balance', 'production_type', 'value_gwh'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in IEA data: {missing}")
    # Drop rows with missing key info
    df = df.dropna(subset=['month', 'country'])
    # Parse 'month' column (e.g., '25-Mar' to '2025-03')
    def parse_custom_date(date_str):
        return pd.to_datetime('20' + date_str, format='%Y-%b')
    df['month'] = df['month'].apply(parse_custom_date).dt.to_period('M').astype(str)
    df = df[df['country'].isin(COUNTRIES)]
    return df

def clean_weather(df):
    # Standardize column names
    if 'Country' in df.columns:
        df = df.rename(columns={'Country': 'country'})
    if 'Month' in df.columns:
        df = df.rename(columns={'Month': 'month'})
    required_cols = {'month', 'country'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in weather data: {missing}")
    df = df.dropna(subset=['month', 'country'])
    df = df[df['country'].isin(COUNTRIES)]
    return df

def merge_data(iea_df, weather_df):
    merged = pd.merge(iea_df, weather_df, on=['country', 'month'], how='left')
    # Ensure columns for downstream scripts
    if 'production_type' not in merged.columns and 'Product' in merged.columns:
        merged = merged.rename(columns={'Product': 'production_type'})
    if 'value_gwh' not in merged.columns and 'Value' in merged.columns:
        merged = merged.rename(columns={'Value': 'value_gwh'})
    return merged

if __name__ == "__main__":
    # Example usage for batch processing
    iea = pd.read_csv('IEA_France_2023_2025.csv')
    weather = pd.read_csv('weather_data.csv')
    iea = clean_iea(iea)
    weather = clean_weather(weather)
    merged = merge_data(iea, weather)
    merged.to_csv(MERGED_DATA_CSV, index=False)
    print(f"Merged data saved to {MERGED_DATA_CSV}")
