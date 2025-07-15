import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import pandas as pd
from analytics.utils import clean_iea, merge_data
from ingestion.ingest_iea import load_iea_data

def test_clean_iea_sample():
    # Test clean_iea with a small sample
    sample = pd.DataFrame({
        'Time': ['23-Jan', '23-Feb'],
        'Country': ['France', 'France'],
        'Product': ['Solar', 'Wind'],
        'Balance': [1, 2],
        'Value': [100, 200]
    })
    countries = ['France']
    cleaned = clean_iea(sample, countries)
    assert 'month' in cleaned.columns
    assert 'country' in cleaned.columns
    assert cleaned['country'].iloc[0] == 'France'

def test_load_iea_data():
    # Test IEA ingestion loads data
    df = load_iea_data()
    assert not df.empty
    assert 'country' in df.columns

def test_merge_data():
    # Test merging two DataFrames on country and month
    df1 = pd.DataFrame({'country': ['France'], 'month': ['2023-01'], 'value_gwh': [100]})
    df2 = pd.DataFrame({'country': ['France'], 'month': ['2023-01'], 'avg_temp_c': [5.0]})
    merged = merge_data(df1, df2)
    assert 'avg_temp_c' in merged.columns
    assert merged.shape[0] == 1

def test_weather_csv_load():
    # Test loading weather data CSV with pandas
    path = 'data/output/weather_data.csv'
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert not df.empty
    assert 'avg_temp_c' in df.columns
