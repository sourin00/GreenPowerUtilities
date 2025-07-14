# forecasting.py
"""
Handles all prediction and forecasting logic, including weather-aware forecasts.
"""
import pandas as pd
import numpy as np
from prophet import Prophet
from sqlalchemy import create_engine
from config import MERGED_DATA_CSV, FORECAST_BY_TYPE_CSV, PROCESSED_WEATHER_COLS, DB_URI

def predict_by_energy_type(input_csv=MERGED_DATA_CSV, output_csv=FORECAST_BY_TYPE_CSV, periods=12):
    df = pd.read_csv(input_csv)
    forecasts = []
    for energy_type, group in df.groupby("production_type"):
        group = group.rename(columns={"month": "ds", "value_gwh": "y"})
        group = group.dropna(subset=["y", "ds"])
        if len(group) < 2:
            continue
        model = Prophet()
        model.fit(group[["ds", "y"]])
        future = model.make_future_dataframe(periods=periods, freq='M')
        forecast = model.predict(future)
        forecast["production_type"] = energy_type
        forecasts.append(forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "production_type"]])
    if forecasts:
        result = pd.concat(forecasts)
        result.to_csv(output_csv, index=False)
        print(f"Saved forecasts by energy type to {output_csv}")
    else:
        print("No forecasts generated. Check your data.")

def predict_by_energy_type_with_weather(input_csv=MERGED_DATA_CSV, output_csv=FORECAST_BY_TYPE_CSV, periods=12):
    df = pd.read_csv(input_csv)
    forecasts = []
    weather_cols = PROCESSED_WEATHER_COLS
    for energy_type, group in df.groupby("production_type"):
        group = group.rename(columns={"month": "ds", "value_gwh": "y"})
        group = group.dropna(subset=["y", "ds"] + weather_cols)
        if len(group) < 2:
            continue
        model = Prophet()
        for col in weather_cols:
            model.add_regressor(col)
        model.fit(group[["ds", "y"] + weather_cols])
        future = model.make_future_dataframe(periods=periods, freq='M')
        for col in weather_cols:
            history_vals = group[col].values
            last_val = history_vals[-1]
            n_history = len(history_vals)
            n_future = len(future)
            if n_future > n_history:
                future_vals = np.concatenate([
                    history_vals,
                    np.full(n_future - n_history, last_val)
                ])
            else:
                future_vals = history_vals[:n_future]
            future[col] = future_vals
        forecast = model.predict(future)
        forecast["production_type"] = energy_type
        forecasts.append(forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "production_type"]])
    if forecasts:
        result = pd.concat(forecasts)
        result.to_csv(output_csv, index=False)
        print(f"Saved forecasts by energy type (with weather) to {output_csv}")
    else:
        print("No forecasts generated. Check your data.")

def fetch_consumption(country="France"):
    engine = create_engine(DB_URI)
    query = f"""
        SELECT month, total_consumption_gwh
        FROM consumption_data
        WHERE country = '{country}'
        ORDER BY month
    """
    df = pd.read_sql(query, engine)
    df = df.rename(columns={"month": "ds", "total_consumption_gwh": "y"})
    df = df.dropna(subset=["y"])
    return df

def predict_peak(df, periods=12):
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods, freq='M')
    forecast = model.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

if __name__ == "__main__":
    predict_by_energy_type()
    predict_by_energy_type_with_weather()
    # National-level forecast
    df = fetch_consumption("France")
    if len(df) < 2:
        raise ValueError("Not enough data to fit the model. Check your database and data extraction.")
    forecast = predict_peak(df)
    forecast.to_csv("forecast_results.csv", index=False)
    print(forecast.tail())
