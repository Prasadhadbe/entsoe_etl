FROM apache/airflow:2.9.0-python3.10

# Copy requirements into the expected location for Airflow to install
COPY requirements.txt /requirements.txt

USER airflow

# These env vars are required for installing custom packages on Airflow startup
ENV AIRFLOW_HOME=/opt/airflow

# Copy DAGs, plugins, config
COPY dags/ ${AIRFLOW_HOME}/dags/
COPY plugins/ ${AIRFLOW_HOME}/plugins/
COPY config/config.yaml ${AIRFLOW_HOME}/config/config.yaml
