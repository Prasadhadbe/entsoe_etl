import os
import psycopg2
from dotenv import load_dotenv
from airflow.decorators import task

load_dotenv()

def load_to_postgres(start_date= None,end_date = None,**kwargs):
    ti = kwargs["ti"]

    transform_task_id = kwargs.get("transform_task_id","transform_data")
    data = ti.xcom_pull(task_ids=transform_task_id)  # <- Use default 'return_value' key

    if not data:
        print(f"🚨 No data received from transform_data task for {start_date} to {end_date}!")
        return

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
        cursor.execute("""
            INSERT INTO day_ahead_prices (country_code, timestamp, price_eur_per_mwh)
            VALUES (%s, %s, %s)
            ON CONFLICT (country_code, timestamp) DO NOTHING;
        """, ('DE', row['timestamp'], row['price_eur_per_mwh']))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Data load complete.")
