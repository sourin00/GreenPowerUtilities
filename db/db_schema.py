from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, text
from config import DB_URI

engine = create_engine(DB_URI)
metadata = MetaData()

# Define tables
power_data = Table(
    "power_data", metadata,
    Column("country", String),
    Column("month", String),
    Column("production_type", String),
    Column("value_gwh", Float)
)

consumption_data = Table(
    "consumption_data", metadata,
    Column("country", String),
    Column("month", String),
    Column("total_consumption_gwh", Float),
    Column("household_consumption_gwh", Float)  # Optional, if you estimate household consumption
)

weather_data = Table(
    "weather_data", metadata,
    Column("country", String),
    Column("month", String),
    Column("avg_temp_c", Float),
    Column("precip_mm", Float),
    Column("wind_kmh", Float)
)

def drop_tables():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS power_data CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS consumption_data CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS weather_data CASCADE"))
        print("All tables dropped.")

def create_tables():
    metadata.create_all(engine)
    print("All tables created.")

if __name__ == "__main__":
    drop_tables()
    create_tables()
    import sys
    sys.exit(0)
