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
    print(f"Command: {cmd}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        print(f"STDOUT for {name}:")
        if result.stdout:
            print(result.stdout)
        print(f"STDERR for {name}:")
        if result.stderr:
            print(result.stderr)
        print(f"{name} completed successfully.")
    except subprocess.TimeoutExpired:
        print(f"Error: {name} timed out.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error in {name}: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected exception in {name}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    for name, cmd in steps:
        print(f"About to run step: {name}")
        try:
            run_step(name, cmd)
        except Exception as e:
            print(f"Exception occurred in step '{name}': {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        print(f"Finished step: {name}")
    print("\nAll pipeline steps completed.")
