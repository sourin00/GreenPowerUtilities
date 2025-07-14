import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import EMISSIONS_FACTORS, PROCESSED_WEATHER_COLS

def clean_iea(df, countries):
    if 'Time' in df.columns:
        df = df.rename(columns={'Time': 'month'})
    if 'Country' in df.columns:
        df = df.rename(columns={'Country': 'country'})
    if 'Product' in df.columns:
        df = df.rename(columns={'Product': 'production_type'})
    if 'Value' in df.columns:
        df = df.rename(columns={'Value': 'value_gwh'})
    required_cols = {'month', 'country', 'Balance', 'production_type', 'value_gwh'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in IEA data: {missing}")
    df = df.dropna(subset=['month', 'country'])
    def parse_custom_date(date_str):
        return pd.to_datetime('20' + date_str, format='%Y-%b')
    df['month'] = df['month'].apply(parse_custom_date).dt.to_period('M').astype(str)
    df = df[df['country'].isin(countries)]
    return df

def clean_weather(df, countries):
    if 'Country' in df.columns:
        df = df.rename(columns={'Country': 'country'})
    if 'Month' in df.columns:
        df = df.rename(columns={'Month': 'month'})
    required_cols = {'month', 'country'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in weather data: {missing}")
    df = df.dropna(subset=['month', 'country'])
    df = df[df['country'].isin(countries)]
    return df

def merge_data(iea_df, weather_df):
    merged = pd.merge(iea_df, weather_df, on=['country', 'month'], how='left')
    if 'production_type' not in merged.columns and 'Product' in merged.columns:
        merged = merged.rename(columns={'Product': 'production_type'})
    if 'value_gwh' not in merged.columns and 'Value' in merged.columns:
        merged = merged.rename(columns={'Value': 'value_gwh'})
    return merged

def detect_anomalies(df, window=12, threshold=3):
    df = df.copy()
    df['zscore'] = (df['value_gwh'] - df['value_gwh'].rolling(window).mean()) / df['value_gwh'].rolling(window).std()
    df['anomaly'] = df['zscore'].abs() > threshold
    return df[df['anomaly']]

def calculate_carbon(df):
    df = df.copy()
    df['emissions_factor'] = df['production_type'].map(EMISSIONS_FACTORS).fillna(EMISSIONS_FACTORS.get('Electricity', 300))
    df['carbon_kg'] = df['value_gwh'] * 1000 * df['emissions_factor']
    return df

def safe_mean(arr1, arr2):
    if arr1 is None or arr2 is None:
        return None
    arr1 = np.array(arr1)
    arr2 = np.array(arr2)
    if arr1.size == 0 or arr2.size == 0:
        return None
    arr1 = np.where(arr1 is None, np.nan, arr1).astype(float)
    arr2 = np.where(arr2 is None, np.nan, arr2).astype(float)
    return np.nanmean(np.vstack([arr1, arr2]), axis=0)

def safe_sum(arr):
    if arr is None:
        return None
    arr = np.array(arr)
    if arr.size == 0:
        return None
    arr = np.where(arr is None, np.nan, arr).astype(float)
    return np.nansum(arr)

