import subprocess
import sys

steps = [
    ("Fetch Power Data", [sys.executable, "-m", "ingestion.ingest_iea"]),
    ("Fetch Weather Data", [sys.executable, "-m", "ingestion.ingest_weather"]),
    ("Ingestion & Transformation", [sys.executable, "-m", "ingestion.clean_transform"]),
    ("Create Schema", [sys.executable, "-m", "db.db_schema"]),
    ("Load to DB", [sys.executable, "-m", "db.load_to_db"]),
    ("Forecasting", [sys.executable, "-m", "analytics.forecasting"]),
    ("Reporting", [sys.executable, "-m", "analytics.reporting"]),
    ("Visualization", [sys.executable, "-m", "analytics.visualization"]),
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
        print(f"About to run step: {name}")
        run_step(name, cmd)
        print(f"Finished step: {name}")
    print("\nAll pipeline steps completed.")
