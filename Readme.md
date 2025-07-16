# GreenPower Project

## Overview
GreenPower is a comprehensive analytics platform for energy consumption and carbon emissions forecasting. It ingests, cleans, analyzes, and visualizes energy and weather data, providing actionable insights and reports for France (2023-2025). The system is modular, scalable, and designed for extensibility.

## Directory Structure
- `analytics/`: Data analytics modules (forecasting, reporting, visualization, utilities)
- `data/`: Input data, output results, and project logo
- `db/`: Database schema and loading scripts
- `ingestion/`: Data ingestion and transformation scripts
- `plots/`: Generated plots and visualizations
- `tests/`: Unit tests for analytics and ingestion
- `config.py`: Configuration settings
- `dashboard.py`: Dashboard interface
- `requirements.txt`: Python dependencies
- `run_pipeline.py`: Main pipeline runner

## Features
### 1. Data Ingestion (`ingestion/`)
- **`ingest_iea.py`**: Loads IEA energy data (France, 2023-2025)
- **`ingest_weather.py`**: Loads weather data
- **`clean_transform.py`**: Cleans and transforms raw data for analysis

### 2. Data Analytics (`analytics/`)
- **`forecasting.py`**: Forecasts energy consumption by type using statistical and ML models
- **`reporting.py`**: Generates carbon emission reports and anomaly detection
- **`visualization.py`**: Creates plots for trends, forecasts, and comparisons
- **`utils.py`**: Helper functions for analytics

### 3. Database Integration (`db/`)
- **`db_schema.py`**: Defines database tables and schema
- **`load_to_db.py`**: Loads processed data into the database

### 4. Dashboard (`dashboard.py`)
- Interactive dashboard for exploring forecasts, emissions, and anomalies

### 5. Plots and Outputs (`plots/`, `data/output/`)
- Visualizations for forecasts, anomalies, carbon emissions, and weather vs consumption
- Output CSVs for processed data and reports

### 6. Testing (`tests/`)
- Unit tests for analytics and ingestion modules

## System Design
- **Data Flow**: Raw data → Ingestion → Cleaning/Transformation → Analytics → Visualization/Reporting → Database/Dashboard
- **Modularity**: Each module is independent and reusable
- **Extensibility**: Easily add new data sources, analytics, or visualizations
- **Automation**: `run_pipeline.py` automates the full workflow

## Setup Instructions
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Prepare input data**: Place CSVs in `data/input/`
4. **Configure settings**: Edit `config.py` as needed

## Usage Guide
- **Run the pipeline**:
  ```bash
  python run_pipeline.py
  ```
- **Start the dashboard**:
  ```bash
  python dashboard.py
  ```
- **View outputs**: Check `data/output/` and `plots/`

## Testing
- Run all tests:
  ```bash
  python -m unittest discover tests
  ```
- Test analytics only:
  ```bash
  python -m unittest tests/test_analytics.py
  ```
- Test ingestion only:
  ```bash
  python -m unittest tests/test_ingestion.py
  ```

## Dependencies
See `requirements.txt` for all required Python packages.
