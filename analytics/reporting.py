"""
Handles all analytics, anomaly detection, carbon tracking, and reporting logic.
"""
import pandas as pd
import numpy as np
import os
import shutil
from config import EMISSIONS_FACTORS, MERGED_DATA_CSV, ANOMALIES_CSV, CARBON_REPORT_CSV, TABLEAU_EXPORT_DIR, FORECAST_BY_TYPE_CSV, PROCESSED_WEATHER_COLS

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

def main():
    df = pd.read_csv(MERGED_DATA_CSV)
    # Anomaly Detection
    anomalies = detect_anomalies(df)
    anomalies.to_csv(ANOMALIES_CSV, index=False)
    print(f"Anomalies saved to {ANOMALIES_CSV}: {len(anomalies)} records.")
    # Carbon Tracking
    carbon_df = calculate_carbon(df)
    carbon_report = carbon_df.groupby('month').agg({'carbon_kg': 'sum'}).reset_index()
    carbon_report.to_csv(CARBON_REPORT_CSV, index=False)
    print(f"Carbon report saved to {CARBON_REPORT_CSV}.")

if __name__ == "__main__":
    main()
