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

if __name__ == "__main__":
    df = fetch_consumption("France")
    if len(df) < 2:
        raise ValueError("Not enough data to fit the model. Check your database and data extraction.")
    forecast = predict_peak(df)
    forecast.to_csv("forecast_results.csv", index=False)
    print(forecast.tail())
