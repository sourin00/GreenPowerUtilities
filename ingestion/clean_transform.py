import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from config import COUNTRIES, MERGED_DATA_CSV, WEATHER_COLS, IEA_CSV, WEATHER_DATA_CSV
from analytics.utils import clean_iea, clean_weather, merge_data

if __name__ == "__main__":
    # Example usage for batch processing
    iea = pd.read_csv(IEA_CSV)
    weather = pd.read_csv(WEATHER_DATA_CSV)
    iea = clean_iea(iea, COUNTRIES)
    weather = clean_weather(weather, COUNTRIES)
    merged = merge_data(iea, weather)
    merged.to_csv(MERGED_DATA_CSV, index=False)
    print(f"Merged data saved to {MERGED_DATA_CSV}")
