import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# Load forecast results by energy type
forecast = pd.read_csv("forecast_by_type.csv")
energy_types = forecast["production_type"].unique()

output_dir = "forecast_plots_by_type"
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
