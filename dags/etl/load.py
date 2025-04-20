# load.py
import os
import psycopg2
from dotenv import load_dotenv
from airflow.decorators import task
from typing import Optional, Dict, Any, List
from datetime import datetime

load_dotenv()

def load_to_postgres(start_date: Optional[str] = None, 
                    end_date: Optional[str] = None,
                    data: Optional[List[Dict]] = None,
                    **kwargs: Dict[str, Any]) -> None:
    """
    Load transformed data into PostgreSQL database.
    Works for both daily and historical loads.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        data: Direct data input (for historical load)
        kwargs: Airflow context (for XCom pull in daily load)
    """
    # Get data either from direct input or XCom
    if data is None:
        ti = kwargs.get("ti")
        if ti is None:
            raise ValueError("Either data or ti must be provided")
        
        transform_task_id = kwargs.get("transform_task_id", "transform_data")
        data = ti.xcom_pull(task_ids=transform_task_id)
        print(f"🧪 Pulled data from task_id='{transform_task_id}': {type(data)} with {len(data) if data else 0} rows")

    
    if not data:
        print(f"🚨 No data received for {start_date} to {end_date}!")
        return
    print(f"Data sample: {data[:1]}")  # Log first row to verify format
    print(f"📦 Loading {len(data)} rows into Postgres from {start_date} to {end_date}...")

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        database=os.getenv("POSTGRES_DB", "airflow"),
        user=os.getenv("POSTGRES_USER", "airflow"),
        password=os.getenv("POSTGRES_PASSWORD", "airflow"),
    )
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS day_ahead_prices (
        id SERIAL PRIMARY KEY,
        country_code VARCHAR(2) NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL,
        price_eur_per_mwh FLOAT,
        UNIQUE (country_code, timestamp)
    );
    """
    cursor.execute(create_table_query)

    for row in data:
        # Handle both dict and list formats
        if isinstance(row, dict):
            timestamp = row['timestamp']
            price = row['price_eur_per_mwh']
            # Convert timestamp string back to datetime if needed
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    print(f"⚠️ Invalid timestamp format: {timestamp}, skipping row.")
                    continue
        elif isinstance(row, (list, tuple)) and len(row) >= 2:
            timestamp = row[0]
            price = row[1]
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    print(f"⚠️ Invalid timestamp format: {timestamp}, skipping row.")
                    continue
        else:
            print(f"⚠️ Skipping malformed row: {row}")
            continue

        cursor.execute("""
            INSERT INTO day_ahead_prices (country_code, timestamp, price_eur_per_mwh)
            VALUES (%s, %s, %s)
            ON CONFLICT (country_code, timestamp) DO NOTHING;
        """, ('DE', timestamp, price))
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Data load complete.")

@task
def load_wrapper(chunk: Dict[str, str], data: List[Dict]) -> None:
    """
    Wrapper function for historical load to work with TaskFlow API.
    
    Args:
        chunk: Dictionary containing start_date and end_date
        data: The transformed data to load
    """
    if not isinstance(data, list):
        print(f"Unexpected data format: {type(data)}")
        return
    print(f"📦 Loading {len(data)} rows for {chunk['start_date']} to {chunk['end_date']}")
    return load_to_postgres(
        start_date=chunk["start_date"],
        end_date=chunk["end_date"],
        data=data
    )