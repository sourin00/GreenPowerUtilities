import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import pandas as pd
from analytics.utils import merge_data
from analytics.reporting import calculate_carbon

def test_merge_data():
    # Test merging two DataFrames on country and month
    df1 = pd.DataFrame({'country': ['France'], 'month': ['2023-01'], 'value_gwh': [100], 'production_type': ['Solar']})
    df2 = pd.DataFrame({'country': ['France'], 'month': ['2023-01'], 'avg_temp_c': [5.0]})
    merged = merge_data(df1, df2)
    assert 'avg_temp_c' in merged.columns
    assert merged.shape[0] == 1

def test_calculate_carbon():
    # Test carbon calculation
    df = pd.DataFrame({'value_gwh': [100], 'production_type': ['Solar']})
    carbon_df = calculate_carbon(df)
    assert 'carbon_kg' in carbon_df.columns
    assert carbon_df['carbon_kg'].iloc[0] > 0
