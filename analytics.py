import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Emissions factors in kg CO2e per MWh (example values, adjust as needed)
EMISSIONS_FACTORS = {
    'Coal, Peat and Manufactured Gases': 820,
    'Oil and Petroleum Products': 650,
    'Natural Gas': 490,
    'Nuclear': 12,
    'Hydro': 24,
    'Wind': 11,
    'Solar': 45,
    'Geothermal': 38,
    'Other Renewables': 30,
    'Combustible Renewables': 230,
    'Other Combustible Non-Renewables': 400,
    'Electricity': 300,  # fallback
    'Not Specified': 300,  # fallback
}

def detect_anomalies(df, window=12, threshold=3):
    df = df.copy()
    df['zscore'] = (df['value_gwh'] - df['value_gwh'].rolling(window).mean()) / df['value_gwh'].rolling(window).std()
    df['anomaly'] = df['zscore'].abs() > threshold
    return df[df['anomaly']]

def calculate_carbon(df):
    df = df.copy()
    df['emissions_factor'] = df['production_type'].map(EMISSIONS_FACTORS).fillna(300)
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

def main():
    df = pd.read_csv('merged_data.csv')
    # Anomaly Detection
    anomalies = detect_anomalies(df)
    anomalies.to_csv('anomalies.csv', index=False)
    print(f"Anomalies saved to anomalies.csv: {len(anomalies)} records.")
    # Carbon Tracking
    carbon_df = calculate_carbon(df)
    carbon_report = carbon_df.groupby('month').agg({'carbon_kg': 'sum'}).reset_index()
    carbon_report.to_csv('carbon_report.csv', index=False)
    print(f"Carbon report saved to carbon_report.csv.")
    # Visualization
    plot_anomalies(anomalies)
    plot_carbon(carbon_report)

if __name__ == "__main__":
    main()
