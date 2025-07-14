import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import shutil
import os
from config import EMISSIONS_FACTORS, MERGED_DATA_CSV, ANOMALIES_CSV, CARBON_REPORT_CSV, TABLEAU_EXPORT_DIR, FORECAST_BY_TYPE_CSV, PROCESSED_WEATHER_COLS

def detect_anomalies(df, window=12, threshold=3):
    df = df.copy()
    df['zscore'] = (df['value_gwh'] - df['value_gwh'].rolling(window).mean()) / df['value_gwh'].rolling(window).std()
    df['anomaly'] = df['zscore'].abs() > threshold
    return df[df['anomaly']]

def calculate_carbon(df):
    df = df.copy()
    df['emissions_factor'] = df['production_type'].map(EMISSIONS_FACTORS).fillna(EMISSIONS_FACTORS.get('Electricity', 300))
    df['carbon_kg'] = df['value_gwh'] * 1000 * df['emissions_factor']  # GWh to MWh
    return df

def plot_anomalies(anomalies):
    if anomalies.empty:
        print("No anomalies to plot.")
        return
    anomalies = anomalies.copy()
    anomalies['month'] = pd.to_datetime(anomalies['month'])
    plt.figure(figsize=(12,6))
    for prod_type in anomalies['production_type'].unique():
        sub = anomalies[anomalies['production_type'] == prod_type]
        plt.scatter(sub['month'], sub['value_gwh'], label=prod_type, s=40)
    plt.xlabel('Month')
    plt.ylabel('Anomalous Consumption (GWh)')
    plt.title('Detected Consumption Anomalies by Energy Type')
    plt.legend()
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid()
    plt.savefig('anomalies_plot.png')
    plt.show()

def plot_carbon(carbon_report):
    carbon_report = carbon_report.copy()
    carbon_report['month'] = pd.to_datetime(carbon_report['month'])
    plt.figure(figsize=(12,6))
    plt.plot(carbon_report['month'], carbon_report['carbon_kg']/1e6, marker='o', color='green')
    plt.xlabel('Month')
    plt.ylabel('Total Carbon Emissions (tonnes)')
    plt.title('Monthly Carbon Emissions from Electricity Consumption')
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid()
    plt.savefig('carbon_emissions_plot.png')
    plt.show()

def plot_weather_vs_consumption(df):
    df = df.copy()
    df['month'] = pd.to_datetime(df['month'])
    fig, axs = plt.subplots(len(PROCESSED_WEATHER_COLS), 1, figsize=(12, 5 * len(PROCESSED_WEATHER_COLS)), sharex=True)
    for i, col in enumerate(PROCESSED_WEATHER_COLS):
        ax = axs[i] if len(PROCESSED_WEATHER_COLS) > 1 else axs
        ax2 = ax.twinx()
        ax.plot(df['month'], df['value_gwh'], color='tab:blue', label='Consumption (GWh)')
        ax2.plot(df['month'], df[col], color='tab:orange', label=col)
        ax.set_ylabel('Consumption (GWh)', color='tab:blue')
        ax2.set_ylabel(col, color='tab:orange')
        ax.set_title(f'Consumption vs {col}')
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.tick_params(axis='x', rotation=45)
        ax.grid()
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('weather_vs_consumption.png')
    plt.show()

def export_for_tableau():
    export_dir = TABLEAU_EXPORT_DIR
    os.makedirs(export_dir, exist_ok=True)
    files_to_export = [
        MERGED_DATA_CSV,
        FORECAST_BY_TYPE_CSV,
        ANOMALIES_CSV,
        CARBON_REPORT_CSV
    ]
    for fname in files_to_export:
        if os.path.exists(fname):
            shutil.copy(fname, os.path.join(export_dir, fname))
    print(f"Exported latest CSVs to {export_dir}/ for Tableau.")

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
    # Visualization
    plot_anomalies(anomalies)
    plot_carbon(carbon_report)
    plot_weather_vs_consumption(df)
    export_for_tableau()

if __name__ == "__main__":
    main()
