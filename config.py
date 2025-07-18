import os
from dotenv import load_dotenv

load_dotenv()
#DB_URI = os.getenv("DB_URI", "postgresql://postgres:123qwe@localhost:5432/green_power") # Local development
DB_URI = os.getenv("DB_URI", "postgresql://postgres.pbbbnfsqfetucbvzixbu:123qwe@aws-0-ap-south-1.pooler.supabase.com:6543/postgres") # Production Supabase

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_INPUT_DIR = os.path.join(BASE_DIR, "data", "input")
DATA_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
FORECAST_PLOTS_DIR = os.path.join(PLOTS_DIR, "forecasts")

MERGED_DATA_CSV = os.path.join(DATA_OUTPUT_DIR, "merged_data.csv")
FORECAST_BY_TYPE_CSV = os.path.join(DATA_OUTPUT_DIR, "forecast_by_type.csv")
FORECAST_RESULTS_CSV = os.path.join(DATA_OUTPUT_DIR, "forecast_results.csv")
ANOMALIES_CSV = os.path.join(DATA_OUTPUT_DIR, "anomalies.csv")
CARBON_REPORT_CSV = os.path.join(DATA_OUTPUT_DIR, "carbon_report.csv")
TABLEAU_EXPORT_DIR = os.path.join(DATA_OUTPUT_DIR, "tableau_exports")
WEATHER_DATA_CSV = os.path.join(DATA_OUTPUT_DIR, "weather_data.csv")
IEA_CSV = os.path.join(DATA_INPUT_DIR, "IEA_France_2023_2025.csv")

COUNTRIES = ["France"]
LOCATIONS = {
    "France": {"lat": 48.8566, "lon": 2.3522}
}
WEATHER_API_BASE = "https://archive-api.open-meteo.com/v1/archive"
START_YEAR = 2010
END_YEAR = 2025

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

# Weather columns for API requests (raw Open-Meteo variable names)
WEATHER_COLS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max"
]
# Processed weather columns for downstream use
PROCESSED_WEATHER_COLS = [
    "avg_temp_c",
    "precip_mm",
    "wind_kmh"
]
