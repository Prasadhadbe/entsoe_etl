from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dags.etl.extract import extract_data
from dags.etl.transform import transform_data
from dags.etl.load import load_to_postgres, load_wrapper
from airflow.decorators import task
from util.utils import get_weekly_chunks
from airflow.decorators import task
from datetime import datetime
from dags.etl.transform import transform_data 
from airflow.models.xcom import LazyXComAccess 
from airflow.operators.python import get_current_context


# deploy test (if dags != changed ? no deploy : deploy new ###)


# Common default arguments for all DAGs
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay":timedelta(minutes=1)
}
current_date = datetime.now()
next_date = current_date + timedelta(days=1)


@task
def generate_chunks():
    chunks = get_weekly_chunks("2024-01-01", datetime.today().strftime("%Y-%m-%d")) # prod 
    # return [{"start_date": "2024-01-01", "end_date": "2024-01-08"}] #(for testing)
    return [{"start_date": c["start_date"], "end_date": c["end_date"]} for c in chunks] # prod

@task
def extract_wrapper(chunk):
    return extract_data(start_date=chunk["start_date"], end_date=chunk["end_date"])


@task
def transform_wrapper(chunk, raw_xml):
    print(f"🔁 Running transform for: {chunk['start_date']} → {chunk['end_date']}")

    if not isinstance(raw_xml, str):
        raise ValueError(f"Expected XML string but got: {type(raw_xml)}")

    print(f"📥 Raw XML received (preview):\n{raw_xml[:500]}...")
    return transform_data(raw_xml)


@task
def transform_daily():
    context = get_current_context()
    ti = context["ti"]

    raw_xml = ti.xcom_pull(task_ids="extract_data")
    if not isinstance(raw_xml, str):
        raise ValueError(f"Expected XML string but got: {type(raw_xml)}")

    print(f"📥 Raw XML received (preview):\n{raw_xml[:500]}...")

    # Transform the XML into structured data
    transformed_data = transform_data(raw_xml)

    # Convert datetime objects to ISO strings (for XCom compatibility)
    for row in transformed_data:
        if isinstance(row.get("timestamp"), datetime):
            row["timestamp"] = row["timestamp"].isoformat()

    return transformed_data


# Daily DAG
with DAG(
    "entsoe_etl_germany_daily",
    default_args=default_args,
    start_date=datetime(2024,1,1),
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
    max_active_tasks=3
) as dag:
    @task
    def extract_daily():
        context = get_current_context()
        return extract_data(
            start_date=context["ds"],
            end_date=context["next_ds"],
            resolution="PT60M"
        )
    
    @task
    def transform_daily(raw_xml):
        if not isinstance(raw_xml, str):
            raise ValueError(f"Expected XML string but got: {type(raw_xml)}")
        return transform_data(raw_xml)
    
    @task
    def load_daily(transformed_data):
        context = get_current_context()
        return load_to_postgres(
            data=transformed_data,
            start_date=context["ds"],
            end_date=context["next_ds"]
        )
    
    # Task flow using TaskFlow API consistently
    raw_data = extract_daily()
    transformed = transform_daily(raw_data)
    load_daily(transformed)

# Historical Backfill DAG
with DAG(
    dag_id="day_ahead_prices_historical",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    start_date=datetime(2024, 1, 1),
    concurrency=300,
    max_active_runs=200,
    max_active_tasks=300,
) as dag:
    # Generate chunks for dynamic mapping
    chunks = generate_chunks()
    # Task flow with explicit names
    extract = extract_wrapper.expand(chunk=chunks)
    transform = transform_wrapper.expand(chunk=chunks, raw_xml=extract)
    load = load_wrapper.expand(chunk=chunks, data= transform)
    
    extract >> transform >> load