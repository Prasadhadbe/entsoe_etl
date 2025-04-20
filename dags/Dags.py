from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_to_postgres, load_wrapper
from airflow.decorators import task
from util.utils import get_weekly_chunks
from airflow.decorators import task
from datetime import datetime
from etl.transform import transform_data  # Assuming it's in a separate module
from airflow.models.xcom import LazyXComAccess 
from airflow.operators.python import get_current_context



# Common default arguments for all DAGs
default_args = {
    "owner": "airflow",
    # "depends_on_past": False,
    # "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}
current_date = datetime.now()
next_date = current_date + timedelta(days=1)


@task
def generate_chunks():
    chunks = get_weekly_chunks("2024-01-01", datetime.today().strftime("%Y-%m-%d"))
    # return [{"start_date": "2024-01-01", "end_date": "2024-01-08"}] (for testing)
    return [{"start_date": c["start_date"], "end_date": c["end_date"]} for c in chunks]

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


# @task
# def transform_wrapper(chunk, raw_xml):
#     context = get_current_context()
#     ti = context["ti"]
#     map_index = context.get("map_index")

#     # 1️⃣ Determine the date range
#     if chunk:  # Historical run
#         start_date = chunk["start_date"]
#         end_date = chunk["end_date"]
#         task_id = "extract_wrapper"
#     else:  # Daily run
#         start_date = end_date = context["ds"]
#         task_id = "extract_data"

#     print(f"🔁 Running transform for: {start_date} → {end_date}")

#     # 2️⃣ Pull XML for current map index
#     raw_xml = ti.xcom_pull(task_ids=task_id, map_indexes=map_index)

#     # 3️⃣ Type check to ensure we don't get LazyXComAccess
#     if not isinstance(raw_xml, str):
#         raise ValueError(f"Expected XML string but got: {type(raw_xml)}")

#     print(f"📥 Raw XML received (preview):\n{raw_xml[:500]}...")

#     # 4️⃣ Transform
#     transformed_data = transform_data(raw_xml)

#     # 5️⃣ Push to XCom for load task
#     ti.xcom_push(key="transformed_data", value=transformed_data)

#     return transformed_data

# @task
# def load_wrapper(chunk):
#     return load_to_postgres(start_date=chunk["start_date"], end_date=chunk["end_date"])


# @task
# def load_to_postgres(chunk):
#     return



# Daily DAG
with DAG(
    "entsoe_etl_germany_daily",
    default_args=default_args,
    start_date=datetime(2024,1,1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    
    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
        op_kwargs={
            "start_date": "{{ ds }}",
            "end_date": "{{ next_ds }}",
            "resolution": "PT60M"
        }
    )

    transform_task = transform_daily()
    # transform_task = PythonOperator(
    #     task_id="transform_data",
    #     python_callable=transform_wrapper,  # No chunk parameter for daily
    # )

    load_task = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_to_postgres,
        op_kwargs={
            "transform_task_id": "transform_daily",
            "start_date": "{{ ds }}",
            "end_date": "{{ next_ds }}"
        }
    )

    extract_task >> transform_task >> load_task

# Historical Backfill DAG
with DAG(
    dag_id="day_ahead_prices_historical",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    start_date=datetime(2024, 1, 1),
) as dag:
    # Generate chunks for dynamic mapping
    chunks = generate_chunks()
    # Task flow with explicit names
    extract = extract_wrapper.expand(chunk=chunks)
    transform = transform_wrapper.expand(chunk=chunks, raw_xml=extract)
    load = load_wrapper.expand(chunk=chunks, data= transform)
    
    extract >> transform >> load