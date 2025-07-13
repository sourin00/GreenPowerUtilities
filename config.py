import os
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI", "postgresql://postgres:123qwe@localhost:5432/green_power")
IEA_CSV = "IEA_France_2023_2025.csv"
COUNTRIES = ["France"]
LOCATIONS = {
    "France": {"lat": 48.8566, "lon": 2.3522}
}
WEATHER_API_BASE = "https://archive-api.open-meteo.com/v1/archive"
START_YEAR = 2010
END_YEAR = 2025
