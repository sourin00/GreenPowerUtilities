import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine
from config import DB_URI

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

def predict_by_energy_type(input_csv="merged_data.csv", output_csv="forecast_by_type.csv", periods=12):
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

if __name__ == "__main__":
    df = fetch_consumption("France")
    if len(df) < 2:
        raise ValueError("Not enough data to fit the model. Check your database and data extraction.")
    forecast = predict_peak(df)
    forecast.to_csv("forecast_results.csv", index=False)
    print(forecast.tail())
    predict_by_energy_type()
