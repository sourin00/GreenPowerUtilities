# visualization.py
"""
Handles all plotting and visualization logic for forecasts, analytics, and weather relationships.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from config import FORECAST_BY_TYPE_CSV, PROCESSED_WEATHER_COLS, PLOTS_DIR, FORECAST_PLOTS_DIR, ANOMALIES_CSV, CARBON_REPORT_CSV, MERGED_DATA_CSV

def plot_forecasts_by_type(forecast_csv=FORECAST_BY_TYPE_CSV, output_dir=FORECAST_PLOTS_DIR):
    forecast = pd.read_csv(forecast_csv)
    energy_types = forecast["production_type"].unique()
    os.makedirs(output_dir, exist_ok=True)
    for energy in energy_types:
        sub = forecast[forecast["production_type"] == energy].copy()
        sub["ds"] = pd.to_datetime(sub["ds"])
        plt.figure(figsize=(12,6))
        plt.plot(sub['ds'], sub['yhat'], label='Forecast', color='blue')
        plt.fill_between(sub['ds'], sub['yhat_lower'], sub['yhat_upper'], color='lightblue', alpha=0.5, label='Prediction Interval')
        plt.xlabel('Month')
        plt.ylabel('Electricity Production (GWh)')
        plt.title(f'Forecasted Electricity Production for France: {energy}')
        plt.legend()
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid()
        plot_path = os.path.join(output_dir, f"forecast_{energy}.png")

        plt.savefig(plot_path)
        plt.close()
        print(f"Saved plot for {energy} to {plot_path}")

def plot_weather_vs_consumption(df, output_file=os.path.join(PLOTS_DIR, "weather_vs_consumption.png")):
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
    plt.savefig(output_file)
    #plt.show()

def plot_anomalies(anomalies, output_file=os.path.join(PLOTS_DIR, "anomalies_plot.png")):
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
    plt.savefig(output_file)
    #plt.show()

def plot_carbon(carbon_report, output_file=os.path.join(PLOTS_DIR, "carbon_emissions_plot.png")):
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
    plt.savefig(output_file)
    #plt.show()

if __name__ == "__main__":
    # Plot forecasts by type if forecast_by_type.csv exists
    if os.path.exists(FORECAST_BY_TYPE_CSV):
        print(f"Generating forecast plots in {FORECAST_PLOTS_DIR} from {FORECAST_BY_TYPE_CSV}")
        plot_forecasts_by_type()
    else:
        print(f"{FORECAST_BY_TYPE_CSV} not found. Skipping forecast plots.")
    # Plot weather vs consumption if merged_data.csv exists
    if os.path.exists(MERGED_DATA_CSV):
        df = pd.read_csv(MERGED_DATA_CSV)
        plot_weather_vs_consumption(df)
    else:
        print(f"{MERGED_DATA_CSV} not found. Skipping weather vs consumption plot.")
    # Plot anomalies if anomalies.csv exists
    if os.path.exists(ANOMALIES_CSV):
        anomalies = pd.read_csv(ANOMALIES_CSV)
        plot_anomalies(anomalies)
    else:
        print(f"{ANOMALIES_CSV} not found. Skipping anomalies plot.")
    # Plot carbon emissions if carbon_report.csv exists
    if os.path.exists(CARBON_REPORT_CSV):
        carbon_report = pd.read_csv(CARBON_REPORT_CSV)
        plot_carbon(carbon_report)
    else:
        print(f"{CARBON_REPORT_CSV} not found. Skipping carbon emissions plot.")
    import sys
    sys.exit(0)
