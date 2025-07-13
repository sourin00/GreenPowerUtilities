import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from config import DB_URI, COUNTRIES

def fetch_data(query):
    engine = create_engine(DB_URI)
    return pd.read_sql(query, engine)

def monthly_summary(country):
    query = f"""
        SELECT month, SUM(value_gwh) as total_gen, SUM(household_consumption_gwh) as household_cons
        FROM power_data
        JOIN consumption_data USING (country, month)
        WHERE country = '{country}'
        GROUP BY month
        ORDER BY month
    """
    return fetch_data(query)

def plot_time_series(df, country):
    plt.figure(figsize=(10,6))
    plt.plot(df["month"], df["total_gen"], label="Total Generation")
    plt.plot(df["month"], df["household_cons"], label="Household Consumption")
    plt.title(f"{country} Power Generation and Consumption")
    plt.xlabel("Month")
    plt.ylabel("GWh")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    for country in COUNTRIES:
        df = monthly_summary(country)
        plot_time_series(df, country)
