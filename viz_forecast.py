import pandas as pd
import matplotlib.pyplot as plt

# Load forecast results
forecast = pd.read_csv("forecast_results.csv")  # or use the DataFrame directly

plt.figure(figsize=(12,6))
plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', color='blue')
plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='lightblue', alpha=0.5, label='Prediction Interval')
plt.xlabel('Month')
plt.ylabel('Electricity Consumption (GWh)')
plt.title('Forecasted Electricity Consumption for France')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
