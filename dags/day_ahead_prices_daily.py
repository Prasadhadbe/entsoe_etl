# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime, timedelta
# from etl.extract import extract_data
# from etl.load import load_data

# def run_daily():
#     today = datetime.utcnow().date()
#     yesterday = today - timedelta(days=1)
#     data = extract_data(datetime.combine(yesterday, datetime.min.time()),
#                         datetime.combine(today, datetime.min.time()))
#     load_data(data)

# with DAG(
#     dag_id="day_ahead_prices_daily",
#     start_date=datetime(2024, 1, 1),
#     schedule_interval="@daily",
#     catchup=False,
# ) as dag:
#     daily_run = PythonOperator(
#         task_id="run_daily",
#         python_callable=run_daily
#     )
