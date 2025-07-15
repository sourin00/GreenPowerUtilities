import streamlit as st
import plotly.express as px
import pandas as pd
import os
from sqlalchemy import create_engine

# Load DB URI from config.py
try:
    from config import DB_URI
except ImportError:
    DB_URI = os.getenv('DB_URI')

def get_power_data():
    engine = create_engine(DB_URI)
    query = "SELECT * FROM power_data;"
    df = pd.read_sql(query, engine)
    return df

def get_consumption_data():
    engine = create_engine(DB_URI)
    query = "SELECT * FROM consumption_data;"
    df = pd.read_sql(query, engine)
    return df

def get_weather_data():
    engine = create_engine(DB_URI)
    query = "SELECT * FROM weather_data;"
    df = pd.read_sql(query, engine)
    return df

anomalies = pd.read_csv('data/output/anomalies.csv')
carbon_report = pd.read_csv('data/output/carbon_report.csv')

df = get_power_data()
consumption_df = get_consumption_data()
weather_df = get_weather_data()

fig = px.histogram(df, x='month', y='value_gwh', color='production_type', barmode='group',
                   title='Monthly Power Production by Type',
                   labels={'value_gwh': 'Power Produced (GWh)', 'month': 'Month', 'production_type': 'Production Type'})

fig_consumption = px.line(consumption_df, x='month', y='total_consumption_gwh', color='country',
                         title='Monthly Total Consumption (GWh)')

if 'avg_temp_c' in weather_df.columns:
    merged_weather = pd.merge(consumption_df, weather_df, on=['country', 'month'], how='left')
    fig_weather = px.scatter(merged_weather, x='avg_temp_c', y='total_consumption_gwh', color='country',
                            title='Weather vs Consumption',
                            labels={'avg_temp_c': 'Average Temperature (C)', 'total_consumption_gwh': 'Total Consumption (GWh)'})
else:
    fig_weather = None

if 'zscore' in anomalies.columns:
    fig_anomalies = px.bar(
        anomalies,
        x='month',
        y='zscore',
        color=anomalies['anomaly'].map({True: 'Anomaly', False: 'Normal'}),
        barmode='group',
        facet_col='production_type' if 'production_type' in anomalies.columns else None,
        title='Z-Score of Power Data by Month (Anomalies Highlighted)',
        labels={'zscore': 'Z-Score', 'month': 'Month', 'color': 'Status'}
    )
else:
    anomalies_true = anomalies[anomalies['anomaly'] == True]
    if not anomalies_true.empty:
        anomalies_count = anomalies_true.groupby(['month', 'production_type']).size().reset_index(name='anomaly_count')
        fig_anomalies = px.bar(anomalies_count, x='month', y='anomaly_count', color='production_type',
                              title='Count of Detected Anomalies in Power Data',
                              labels={'anomaly_count': 'Anomaly Count', 'month': 'Month', 'production_type': 'Production Type'})
    else:
        fig_anomalies = None

carbon_summary = carbon_report if not carbon_report.empty else pd.DataFrame()
summary = df.groupby(['month', 'production_type'])['value_gwh'].sum().reset_index()

if not carbon_report.empty and 'month' in carbon_report.columns and 'carbon_kg' in carbon_report.columns:
    fig_carbon = px.bar(
        carbon_report,
        x='month',
        y='carbon_kg',
        barmode='group',
        title='Monthly Carbon Emissions',
        labels={'carbon_kg': 'Carbon Emissions (kg)', 'month': 'Month'}
    )
else:
    fig_carbon = None

forecast_total_path = 'data/output/forecast_results.csv'
forecast_type_path = 'data/output/forecast_by_type.csv'
fig_forecast_total = None
fig_forecast_type = None

if os.path.exists(forecast_total_path):
    forecast_total = pd.read_csv(forecast_total_path)
    if 'ds' in forecast_total.columns and 'yhat' in forecast_total.columns:
        fig_forecast_total = px.line(
            forecast_total,
            x='ds',
            y='yhat',
            title='Total Power Forecast',
            labels={'yhat': 'Forecasted Power (GWh)', 'ds': 'Month'}
        )
        if 'yhat_upper' in forecast_total.columns and 'yhat_lower' in forecast_total.columns:
            fig_forecast_total.add_traces([
                px.line(forecast_total, x='ds', y='yhat_upper').data[0],
                px.line(forecast_total, x='ds', y='yhat_lower').data[0]
            ])
            fig_forecast_total.data[1].name = 'Upper Bound'
            fig_forecast_total.data[2].name = 'Lower Bound'

if os.path.exists(forecast_type_path):
    forecast_type = pd.read_csv(forecast_type_path)
    if 'ds' in forecast_type.columns and 'yhat' in forecast_type.columns and 'production_type' in forecast_type.columns:
        fig_forecast_type = px.line(
            forecast_type,
            x='ds',
            y='yhat',
            color='production_type',
            title='Power Forecast by Production Type',
            labels={'yhat': 'Forecasted Power (GWh)', 'ds': 'Month', 'production_type': 'Production Type'}
        )
        if 'yhat_upper' in forecast_type.columns and 'yhat_lower' in forecast_type.columns:
            for prod_type in forecast_type['production_type'].unique():
                subset = forecast_type[forecast_type['production_type'] == prod_type]
                fig_forecast_type.add_traces([
                    px.line(subset, x='ds', y='yhat_upper').data[0],
                    px.line(subset, x='ds', y='yhat_lower').data[0]
                ])
                fig_forecast_type.data[-2].name = f'{prod_type} Upper Bound'
                fig_forecast_type.data[-1].name = f'{prod_type} Lower Bound'

fig_forecasted_carbon = None
if 'forecast_total' in locals() and not forecast_total.empty and 'ds' in forecast_total.columns and 'yhat' in forecast_total.columns:
    if not carbon_report.empty and 'carbon_kg' in carbon_report.columns and 'month' in carbon_report.columns:
        if 'month' in df.columns and 'value_gwh' in df.columns:
            merged_hist = pd.merge(
                carbon_report, df.groupby('month')['value_gwh'].sum().reset_index(),
                on='month', how='inner')
            merged_hist = merged_hist[merged_hist['value_gwh'] > 0]
            if not merged_hist.empty:
                avg_carbon_intensity = merged_hist['carbon_kg'].sum() / merged_hist['value_gwh'].sum()
            else:
                avg_carbon_intensity = 0
        else:
            avg_carbon_intensity = 0
    else:
        avg_carbon_intensity = 0
    forecasted_carbon = forecast_total.copy()
    forecasted_carbon['forecasted_carbon_kg'] = forecasted_carbon['yhat'] * avg_carbon_intensity
    fig_forecasted_carbon = px.line(
        forecasted_carbon,
        x='ds',
        y='forecasted_carbon_kg',
        title='Forecasted Carbon Emissions',
        labels={'forecasted_carbon_kg': 'Forecasted Carbon Emissions (kg)', 'ds': 'Month'}
    )

# --- Streamlit Layout ---
st.set_page_config(page_title='GreenPower Dashboard', layout='wide', page_icon=':bar_chart:')
st.markdown('<style>div.block-container{padding-top:2rem;} .stHeader {color:#2E8B57;} .st-emotion-cache-1v0mbdj {background: #f5f7fa;} .st-emotion-cache-1v0mbdj h1 {color: #2E8B57;} .st-emotion-cache-1v0mbdj h2 {color: #1976D2;} .st-emotion-cache-1v0mbdj h3 {color: #388E3C;} .st-emotion-cache-1v0mbdj h4 {color: #F57C00;} .st-emotion-cache-1v0mbdj h5 {color: #C62828;} .st-emotion-cache-1v0mbdj h6 {color: #6D4C41;} .stDataFrame {background: #f9f9f9; border-radius: 10px; box-shadow: 0 2px 8px #b2dfdb;} .stPlotlyChart {background: #fff; border-radius: 10px; box-shadow: 0 2px 8px #b2dfdb;}</style>', unsafe_allow_html=True)
st.title('GreenPower Data Dashboard')
st.markdown('''<div style="font-size:18px; color:#444; background:#e3f2fd; border-radius:8px; padding:18px 24px; margin-bottom:30px; border-left: 6px solid #1976D2;">\
<b>Welcome!</b> This dashboard provides a <b>comprehensive overview</b> of power generation, consumption, weather impact, anomalies, carbon emissions, and forecasts for energy data.<br>\
Use the visualizations and tables below to <b>explore trends</b>, <b>detect issues</b>, and <b>support data-driven decisions</b>.<br>\
</div>''', unsafe_allow_html=True)

# Add a sidebar with logo and navigation
if os.path.exists('data/logo.png'):
    st.sidebar.image('data/logo.png', width=80)
else:
    st.sidebar.text("Logo not found")
st.sidebar.title('GreenPower Utilities')
st.sidebar.markdown('''---\n**Navigation**\n- Overview\n- Production\n- Consumption\n- Weather\n- Anomalies\n- Carbon\n- Forecasts\n''')

# --- Section: Power Production Distribution ---
st.header('⚡ Power Production Distribution')
st.write('Visualizes the monthly distribution of power production by type. Use this to identify which energy sources contribute most to the grid and how production varies over time.')
st.plotly_chart(fig, use_container_width=True)

# --- Section: Monthly Production Summary ---
st.header('📊 Monthly Production Summary')
st.write('Tabular summary of total power produced each month, broken down by production type. Useful for quick comparisons and reporting.')
st.dataframe(summary, use_container_width=True, hide_index=True)

# --- Section: Monthly Consumption ---
st.header('🔌 Monthly Consumption')
st.write('Shows the total electricity consumption per month for each country. Track demand trends and seasonal patterns.')
st.plotly_chart(fig_consumption, use_container_width=True)

# --- Section: Weather vs Consumption ---
st.header('🌦️ Weather vs Consumption')
st.write('Examines the relationship between average temperature and electricity consumption. Helps understand how weather impacts energy demand.')
if fig_weather:
    st.plotly_chart(fig_weather, use_container_width=True)
else:
    st.info('Weather data not available.')

# --- Section: Anomalies in Power Data ---
st.header('🚨 Anomalies in Power Data')
st.write('Highlights unusual or unexpected values in power data using statistical anomaly detection. Use this to quickly spot data quality issues or operational outliers.')
if fig_anomalies:
    st.plotly_chart(fig_anomalies, use_container_width=True)
else:
    st.info('Anomaly data not available.')

# --- Section: Carbon Emissions ---
st.header('🌱 Carbon Emissions')
st.write('Displays the monthly carbon emissions associated with power production. Track progress towards sustainability and emissions reduction goals.')
if fig_carbon:
    st.plotly_chart(fig_carbon, use_container_width=True)
else:
    st.info('Carbon emissions data not available.')

# --- Section: Carbon Emissions Report ---
st.header('📋 Carbon Emissions Report')
st.write('Detailed table of carbon emissions data for further analysis and reporting.')
if not carbon_summary.empty:
    st.dataframe(carbon_summary, use_container_width=True, hide_index=True)
else:
    st.info('Carbon report not available.')

# --- Section: Raw Power Data ---
st.header('🗃️ Raw Power Data')
st.write('Full raw power data for transparency and custom analysis. Use filters and sorting to explore the dataset.')
st.dataframe(df, use_container_width=True, hide_index=True)

# --- Section: Forecasts ---
st.header('🔮 Forecasts')
st.write('Forecasts future power production using statistical models. Includes uncertainty intervals to support planning and risk assessment.')
if fig_forecast_total:
    st.plotly_chart(fig_forecast_total, use_container_width=True)
else:
    st.info('Total forecast data not available.')
if fig_forecast_type:
    st.plotly_chart(fig_forecast_type, use_container_width=True)
else:
    st.info('Forecast by type data not available.')

# --- Section: Forecasted Carbon Emissions ---
st.header('🌍 Forecasted Carbon Emissions')
st.write('This graph estimates future carbon emissions based on forecasted power production and average historical carbon intensity. Use it to visualize the expected impact of decarbonization efforts and energy transition policies.')
if fig_forecasted_carbon:
    st.plotly_chart(fig_forecasted_carbon, use_container_width=True)
else:
    st.info('Forecasted carbon emissions data not available.')
