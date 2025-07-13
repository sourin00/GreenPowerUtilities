Install dependencies:

bash
pip install -r requirements.txt
Set up your .env file with the correct database URI.

Run the scripts in the recommended order:

ingest_iea.py

ingest_weather.py

clean_transform.py

db_schema.py

load_to_db.py

Use reporting.py and predict.py for analytics and predictions.