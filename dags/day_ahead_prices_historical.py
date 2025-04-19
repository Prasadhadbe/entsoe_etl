# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime, timedelta
# from etl.extract import extract_data
# from etl.load import load_data

# def backfill():
#     start = datetime(2024, 1, 1)
#     end = datetime.now()
#     current = start

#     while current < end:
#         next_day = current + timedelta(days=1)
#         print(f"Fetching {current} → {next_day}")
#         data = extract_data(current, next_day)
#         load_data(data)
#         current = next_day

# with DAG(
#     dag_id="day_ahead_prices_historical",
#     start_date=datetime(2024, 1, 1),
#     schedule_interval=None,  # manual run
#     catchup=False,
# ) as dag:
#     run_backfill = PythonOperator(
#         task_id="run_backfill",
#         python_callable=backfill
#     )
