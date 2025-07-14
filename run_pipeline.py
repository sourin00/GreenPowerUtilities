import subprocess
import sys

steps = [
    ("Fetch Power Data", [sys.executable, "ingestion/ingest_iea.py"]),
    ("Fetch Weather Data", [sys.executable, "ingestion/ingest_weather.py"]),
    ("Ingestion & Transformation", [sys.executable, "ingestion/clean_transform.py"]),
    ("Create Schema", [sys.executable, "db/db_schema.py"]),
    ("Load to DB", [sys.executable, "db/load_to_db.py"]),
    ("Forecasting", [sys.executable, "analytics/forecasting.py"]),
    ("Reporting", [sys.executable, "analytics/reporting.py"]),
    ("Visualization", [sys.executable, "analytics/visualization.py"]),
]


def run_step(name, cmd):
    print(f"\n=== Running: {name} ===")
    try:
        result = subprocess.run(cmd, check=True)
        print(f"{name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error in {name}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    for name, cmd in steps:
        run_step(name, cmd)
    print("\nPipeline execution complete.")
