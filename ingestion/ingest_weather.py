from calendar import monthrange
from datetime import datetime

import numpy as np
import pandas as pd
import requests

from config import WEATHER_API_BASE, LOCATIONS, START_YEAR, END_YEAR, COUNTRIES, WEATHER_COLS, PROCESSED_WEATHER_COLS, WEATHER_DATA_CSV

CURRENT_DATE = datetime.strptime("2025-07-13", "%Y-%m-%d")


def should_skip_month(year, month, current_date):
    start_date = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = datetime(year, month, last_day)
    if end_date > current_date:
        end_date = current_date
    return end_date < start_date

def safe_mean(arr1, arr2):
    if arr1 is None or arr2 is None:
        return None
    arr1 = np.array(arr1)
    arr2 = np.array(arr2)
    if arr1.size == 0 or arr2.size == 0:
        return None
    arr1 = np.where(arr1 is None, np.nan, arr1).astype(float)
    arr2 = np.where(arr2 is None, np.nan, arr2).astype(float)
    return np.nanmean(np.vstack([arr1, arr2]), axis=0)


def safe_sum(arr):
    if arr is None:
        return None
    arr = np.array(arr)
    if arr.size == 0:
        return None
    arr = np.where(arr is None, np.nan, arr).astype(float)
    return np.nansum(arr)


def adjust_end_date(year, month, current_date):
    last_day = monthrange(year, month)[1]
    end_date = datetime(year, month, last_day)
    if end_date > current_date:
        end_date = current_date
        last_iteration = True
    else:
        last_iteration = False
    return end_date.strftime("%Y-%m-%d"), last_iteration


def fetch_weather(country, lat, lon):
    records = []
    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):
            if should_skip_month(year, month, CURRENT_DATE):
                print(f"Skipping {year}-{month:02d} as it is in the future.")
                continue
            start_date = f"{year}-{month:02d}-01"
            end_date, last_iteration = adjust_end_date(year, month, CURRENT_DATE)
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": WEATHER_COLS,
                "timezone": "Europe/Paris"
            }
            print(f"Requesting weather data for {country} {year}-{month:02d} from {start_date} to {end_date}...")
            resp = requests.get(WEATHER_API_BASE, params=params)
            data = resp.json()
            if 'daily' not in data:
                print(f"API error for {country} {year}-{month:02d}: {data}")
                if last_iteration:
                    break
                else:
                    continue
            daily = data['daily']
            # Compute processed weather columns
            avg_temp = None
            if 'temperature_2m_max' in daily and 'temperature_2m_min' in daily:
                avg_temp = safe_mean(daily["temperature_2m_max"], daily["temperature_2m_min"])
            precip_mm = safe_sum(daily.get("precipitation_sum"))
            wind_kmh = np.nanmean(np.array(daily.get("wind_speed_10m_max", []), dtype=float))
            records.append({
                "country": country,
                "month": f"{year}-{month:02d}",
                "avg_temp_c": float(np.mean(avg_temp)) if avg_temp is not None else None,
                "precip_mm": float(precip_mm) if precip_mm is not None else None,
                "wind_kmh": float(wind_kmh) if not np.isnan(wind_kmh) else None
            })
    print(f"Fetched weather data for {country}.")
    return pd.DataFrame(records)


def main():
    print("Starting weather data ingestion...")
    dfs = []
    for country, loc in LOCATIONS.items():
        if country != "France":
            continue
        print(f"Processing country: {country}")
        df = fetch_weather(country, loc["lat"], loc["lon"])
        dfs.append(df)
    weather_df = pd.concat(dfs, ignore_index=True)
    print(f"Saving weather data to {WEATHER_DATA_CSV}...")
    weather_df.to_csv(WEATHER_DATA_CSV, index=False)
    print("Weather data ingestion completed.")


if __name__ == "__main__":
    main()
    import sys
    sys.exit(0)
