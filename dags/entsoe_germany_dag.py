from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_to_postgres



# Set your static custom start and end dates here
custom_start_date = datetime(2024, 4, 1)
custom_end_date = datetime(2024, 4, 2)
resolution = "PT60M"  # Data collection time intervel

# # 15-minute intervals
# resolution = "PT15M"

# # Hourly intervals
# resolution = "PT60M"

# # Daily intervals
# resolution = "P1D"

# # Weekly intervals
# resolution = "P7D"


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    "entsoe_etl_germany",
    default_args=default_args,
    description="ETL pipeline to fetch ENTSOE data for Germany and load to Postgres",
    schedule_interval="@daily",
    catchup=True,  # for backfilling historical data
    tags=["entsoe", "germany"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
        op_kwargs= {
            "start_date": custom_start_date,
            "end_date": custom_end_date,
            "resolution": resolution
        }
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    load_task = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_to_postgres,
    )

    extract_task >> transform_task >> load_task
