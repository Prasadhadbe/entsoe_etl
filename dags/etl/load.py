import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def load_to_postgres(**kwargs):
    ti = kwargs["ti"]
    data = ti.xcom_pull(task_ids="transform_data")  # <- Use default 'return_value' key

    if not data:
        print("🚨 No data received from transform_data task!")
        return

    print(f"📦 Loading {len(data)} rows into Postgres...")

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
