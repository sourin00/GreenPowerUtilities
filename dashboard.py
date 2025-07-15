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
    query = "SELECT * FROM power_data LIMIT 1000;"
    df = pd.read_sql(query, engine)
    return df

# Fetch data
df = get_power_data()

# Only use the numeric column for the histogram, grouped by month
fig = px.histogram(df, x='month', y='value_gwh', color='production_type', barmode='group',
                   title='Monthly Power Production by Type',
                   labels={'value_gwh': 'Power Produced (GWh)', 'month': 'Month', 'production_type': 'Production Type'})

# Add a summary table by month and production_type
summary = df.groupby(['month', 'production_type'])['value_gwh'].sum().reset_index()

# Dash app layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('Power Data Dashboard'),
    dcc.Graph(figure=fig),
    html.H2('Monthly Production Summary'),
    dash_table.DataTable(
        data=summary.to_dict('records'),
        columns=[{"name": i, "id": i} for i in summary.columns],
        page_size=20,
        style_table={'overflowX': 'auto'}
    ),
    html.H2('Raw Data'),
    dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=20,
        style_table={'overflowX': 'auto'}
    )
])

if __name__ == '__main__':
    app.run(debug=True)
