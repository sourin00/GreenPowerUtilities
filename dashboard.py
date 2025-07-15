import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os

# Load DB URI from config.py
try:
    from config import DB_URI
except ImportError:
    DB_URI = os.getenv('DB_URI')

# Connect to Supabase/PostgreSQL
def get_power_data():
    engine = create_engine(DB_URI)
    query = "SELECT * FROM power_data;"
    df = pd.read_sql(query, engine)
    return df

# Fetch additional data from the database
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

# Fetch additional generated data from CSVs
anomalies = pd.read_csv('data/output/anomalies.csv')
carbon_report = pd.read_csv('data/output/carbon_report.csv')

# Debug: Print columns and sample of carbon_report
print('carbon_report columns:', carbon_report.columns.tolist())
print('carbon_report sample:', carbon_report.head())

# Fetch data
df = get_power_data()
consumption_df = get_consumption_data()
weather_df = get_weather_data()

# Only use the numeric column for the histogram, grouped by month
fig = px.histogram(df, x='month', y='value_gwh', color='production_type', barmode='group',
                   title='Monthly Power Production by Type',
                   labels={'value_gwh': 'Power Produced (GWh)', 'month': 'Month', 'production_type': 'Production Type'})

# Consumption time series plot
fig_consumption = px.line(consumption_df, x='month', y='total_consumption_gwh', color='country',
                         title='Monthly Total Consumption (GWh)')

# Weather vs Consumption scatter plot
if 'avg_temp_c' in weather_df.columns:
    merged_weather = pd.merge(consumption_df, weather_df, on=['country', 'month'], how='left')
    fig_weather = px.scatter(merged_weather, x='avg_temp_c', y='total_consumption_gwh', color='country',
                            title='Weather vs Consumption',
                            labels={'avg_temp_c': 'Average Temperature (C)', 'total_consumption_gwh': 'Total Consumption (GWh)'})
else:
    fig_weather = None

# Anomalies plot using zscore, highlighting anomalies
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
    # fallback to count plot if zscore not present
    anomalies_true = anomalies[anomalies['anomaly'] == True]
    if not anomalies_true.empty:
        anomalies_count = anomalies_true.groupby(['month', 'production_type']).size().reset_index(name='anomaly_count')
        fig_anomalies = px.bar(anomalies_count, x='month', y='anomaly_count', color='production_type',
                              title='Count of Detected Anomalies in Power Data',
                              labels={'anomaly_count': 'Anomaly Count', 'month': 'Month', 'production_type': 'Production Type'})
    else:
        fig_anomalies = None

# Carbon report summary table
carbon_summary = carbon_report if not carbon_report.empty else pd.DataFrame()

# Add a summary table by month and production_type
summary = df.groupby(['month', 'production_type'])['value_gwh'].sum().reset_index()

# Carbon emissions plot (if available)
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

# --- Forecasting Graphs ---
# Try to load forecast results (total and by type)
forecast_total_path = 'data/output/forecast_results.csv'
forecast_type_path = 'data/output/forecast_by_type.csv'
fig_forecast_total = None
fig_forecast_type = None

if os.path.exists(forecast_total_path):
    forecast_total = pd.read_csv(forecast_total_path)
    print('forecast_total columns:', forecast_total.columns.tolist())
    print('forecast_total sample:', forecast_total.head())
    if 'ds' in forecast_total.columns and 'yhat' in forecast_total.columns:
        fig_forecast_total = px.line(
            forecast_total,
            x='ds',
            y='yhat',
            title='Total Power Forecast',
            labels={'yhat': 'Forecasted Power (GWh)', 'ds': 'Month'}
        )
        # Add uncertainty interval
        fig_forecast_total.add_traces([
            px.line(forecast_total, x='ds', y='yhat_upper').data[0],
            px.line(forecast_total, x='ds', y='yhat_lower').data[0]
        ])
        fig_forecast_total.data[1].name = 'Upper Bound'
        fig_forecast_total.data[2].name = 'Lower Bound'

if os.path.exists(forecast_type_path):
    forecast_type = pd.read_csv(forecast_type_path)
    print('forecast_type columns:', forecast_type.columns.tolist())
    print('forecast_type sample:', forecast_type.head())
    if 'ds' in forecast_type.columns and 'yhat' in forecast_type.columns and 'production_type' in forecast_type.columns:
        fig_forecast_type = px.line(
            forecast_type,
            x='ds',
            y='yhat',
            color='production_type',
            title='Power Forecast by Production Type',
            labels={'yhat': 'Forecasted Power (GWh)', 'ds': 'Month', 'production_type': 'Production Type'}
        )
        # Add uncertainty interval for each production_type
        for prod_type in forecast_type['production_type'].unique():
            subset = forecast_type[forecast_type['production_type'] == prod_type]
            fig_forecast_type.add_traces([
                px.line(subset, x='ds', y='yhat_upper').data[0],
                px.line(subset, x='ds', y='yhat_lower').data[0]
            ])
            fig_forecast_type.data[-2].name = f'{prod_type} Upper Bound'
            fig_forecast_type.data[-1].name = f'{prod_type} Lower Bound'

# --- Forecasted Carbon Emissions Graph ---
# Estimate future carbon emissions based on forecasted power production
fig_forecasted_carbon = None
if not forecast_total.empty and 'ds' in forecast_total.columns and 'yhat' in forecast_total.columns:
    # Calculate average carbon intensity from historical data
    if not carbon_report.empty and 'carbon_kg' in carbon_report.columns and 'month' in carbon_report.columns:
        # Try to get matching power data for the same months
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
    # Estimate forecasted carbon emissions
    forecasted_carbon = forecast_total.copy()
    forecasted_carbon['forecasted_carbon_kg'] = forecasted_carbon['yhat'] * avg_carbon_intensity
    fig_forecasted_carbon = px.line(
        forecasted_carbon,
        x='ds',
        y='forecasted_carbon_kg',
        title='Forecasted Carbon Emissions',
        labels={'forecasted_carbon_kg': 'Forecasted Carbon Emissions (kg)', 'ds': 'Month'}
    )

# Dash app layout
app = dash.Dash(__name__)
app.title = 'GreenPower Dashboard'
app.layout = html.Div([
    html.H1('GreenPower Data Dashboard', style={'textAlign': 'center', 'color': '#2E8B57', 'marginTop': 20}),
    html.P(
        'This dashboard provides a comprehensive overview of power generation, consumption, weather impact, anomalies, carbon emissions, and forecasts for energy data. Use the visualizations and tables below to explore trends, detect issues, and support data-driven decisions.',
        style={'textAlign': 'center', 'color': '#333', 'fontSize': '18px', 'marginBottom': '30px'}
    ),
    html.Div([
        html.H2('Power Production Distribution', style={'color': '#1976D2'}),
        html.P('Visualizes the monthly distribution of power production by type. Use this to identify which energy sources contribute most to the grid and how production varies over time.', style={'color': '#333'}),
        dcc.Graph(figure=fig, style={'backgroundColor': '#f9f9f9', 'borderRadius': '10px', 'boxShadow': '0 2px 8px #b2dfdb'}),
    ], style={'margin': '30px 0'}),
    html.H2('Monthly Production Summary', style={'color': '#1976D2'}),
    html.P('Tabular summary of total power produced each month, broken down by production type. Useful for quick comparisons and reporting.', style={'color': '#333'}),
    dash_table.DataTable(
        data=summary.to_dict('records'),
        columns=[{"name": i, "id": i} for i in summary.columns],
        page_size=20,
        style_table={'overflowX': 'auto', 'backgroundColor': '#f1f8e9', 'borderRadius': '10px'},
        style_header={'backgroundColor': '#1976D2', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        style_data={'backgroundColor': '#e3f2fd'},
    ),
    html.H2('Monthly Consumption', style={'color': '#388E3C'}),
    html.P('Shows the total electricity consumption per month for each country. Track demand trends and seasonal patterns.', style={'color': '#333'}),
    dcc.Graph(figure=fig_consumption, style={'backgroundColor': '#f9fbe7', 'borderRadius': '10px', 'boxShadow': '0 2px 8px #b2dfdb'}),
    html.H2('Weather vs Consumption', style={'color': '#F57C00'}),
    html.P('Examines the relationship between average temperature and electricity consumption. Helps understand how weather impacts energy demand.', style={'color': '#333'}),
    dcc.Graph(figure=fig_weather, style={'backgroundColor': '#fff3e0', 'borderRadius': '10px', 'boxShadow': '0 2px 8px #ffe0b2'}) if fig_weather else html.Div('Weather data not available.'),
    html.H2('Anomalies in Power Data', style={'color': '#C62828'}),
    html.P('Highlights unusual or unexpected values in power data using statistical anomaly detection. Use this to quickly spot data quality issues or operational outliers.', style={'color': '#333'}),
    dcc.Graph(figure=fig_anomalies, style={'backgroundColor': '#ffebee', 'borderRadius': '10px', 'boxShadow': '0 2px 8px #ffcdd2'}) if fig_anomalies else html.Div('Anomaly data not available.'),
    html.H2('Carbon Emissions', style={'color': '#6D4C41'}),
    html.P('Displays the monthly carbon emissions associated with power production. Track progress towards sustainability and emissions reduction goals.', style={'color': '#333'}),
    dcc.Graph(figure=fig_carbon, style={'backgroundColor': '#efebe9', 'borderRadius': '10px', 'boxShadow': '0 2px 8px #bcaaa4'}) if fig_carbon else html.Div('Carbon emissions data not available.'),
    html.H2('Carbon Emissions Report', style={'color': '#6D4C41'}),
    html.P('Detailed table of carbon emissions data for further analysis and reporting.', style={'color': '#333'}),
    dash_table.DataTable(
        data=carbon_summary.to_dict('records'),
        columns=[{"name": i, "id": i} for i in carbon_summary.columns] if not carbon_summary.empty else [],
        page_size=20,
        style_table={'overflowX': 'auto', 'backgroundColor': '#fbe9e7', 'borderRadius': '10px'},
        style_header={'backgroundColor': '#6D4C41', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        style_data={'backgroundColor': '#ffccbc'},
    ) if not carbon_summary.empty else html.Div('Carbon report not available.'),
    html.H2('Raw Power Data', style={'color': '#512DA8'}),
    html.P('Full raw power data for transparency and custom analysis. Use filters and sorting to explore the dataset.', style={'color': '#333'}),
    dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=20,
        style_table={'overflowX': 'auto', 'backgroundColor': '#ede7f6', 'borderRadius': '10px'},
        style_header={'backgroundColor': '#512DA8', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'center', 'padding': '8px'},
        style_data={'backgroundColor': '#d1c4e9'},
    ),
    html.H2('Forecasts', style={'color': '#0288D1'}),
    html.P('Forecasts future power production using statistical models. Includes uncertainty intervals to support planning and risk assessment.', style={'color': '#333'}),
    dcc.Graph(figure=fig_forecast_total, style={'backgroundColor': '#e1f5fe', 'borderRadius': '10px', 'boxShadow': '0 2px 8px #b3e5fc'}) if fig_forecast_total else html.Div('Total forecast data not available.'),
    dcc.Graph(figure=fig_forecast_type, style={'backgroundColor': '#e1f5fe', 'borderRadius': '10px', 'boxShadow': '0 2px 8px #b3e5fc'}) if fig_forecast_type else html.Div('Forecast by type data not available.'),
    html.H2('Forecasted Carbon Emissions', style={'color': '#009688'}),
    html.P('This graph estimates future carbon emissions based on forecasted power production and average historical carbon intensity. Use it to visualize the expected impact of decarbonization efforts and energy transition policies.', style={'color': '#333'}),
    dcc.Graph(figure=fig_forecasted_carbon, style={'backgroundColor': '#e0f2f1', 'borderRadius': '10px', 'boxShadow': '0 2px 8px #80cbc4'}) if fig_forecasted_carbon else html.Div('Forecasted carbon emissions data not available.'),
], style={'fontFamily': 'Segoe UI, Arial, sans-serif', 'backgroundColor': '#fafafa', 'padding': '20px 40px'})

if __name__ == '__main__':
    app.run(debug=True)
