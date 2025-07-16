import pandas as pd
from sqlalchemy import create_engine
from config import DB_URI, MERGED_DATA_CSV, COUNTRIES, WEATHER_COLS, PROCESSED_WEATHER_COLS

# Load merged data
merged = pd.read_csv(MERGED_DATA_CSV)

# --- POWER DATA ---
# Debug: Check unique values in Balance and country
print('Unique Balance values:', merged['Balance'].unique())
print('Unique country values:', merged['country'].unique())

# Select production rows (e.g., Balance == 'Net Electricity Production')
power = merged[
    (merged['country'].isin(COUNTRIES)) &
    (merged['Balance'].str.strip().str.lower() == 'net electricity production'.lower())
][["country", "month", "production_type", "value_gwh"]]
print('Filtered power shape:', power.shape)
print('Sample power data:', power.head())

# --- CONSUMPTION DATA ---
# Select total consumption rows (e.g., Balance == 'Final Consumption Calculated')
consumption = merged[
    (merged['country'].isin(COUNTRIES)) &
    (merged['Balance'].str.strip() == 'Final Consumption (Calculated)')
][["country", "month", "value_gwh"]].rename(columns={'value_gwh': 'total_consumption_gwh'})

# Estimate household consumption (optional, adjust ratio as needed)
consumption['household_consumption_gwh'] = consumption['total_consumption_gwh'] * 0.3

# --- WEATHER DATA ---
# Select relevant weather columns (these may already be merged for each month)
weather = merged[PROCESSED_WEATHER_COLS + ["country", "month"]].drop_duplicates()

# --- LOAD TO DATABASE ---
engine = create_engine(DB_URI)

# Load each DataFrame to the appropriate table
print(power.shape)
power.to_sql("power_data", engine, if_exists="append", index=False)
consumption.to_sql("consumption_data", engine, if_exists="append", index=False)
weather.to_sql("weather_data", engine, if_exists="append", index=False)

print("Data loaded successfully into TimescaleDB.")
