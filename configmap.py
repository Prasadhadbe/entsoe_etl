# # values.yaml
# extraEnv:
#   - name: AIRFLOW__CORE__SQL_ALCHEMY_CONN
#     value: "postgresql+psycopg2://airflow:MyStrongPassword123@16063PG_NAME.postgres.database.azure.com/airflow"
#   - name: AIRFLOW__WEBSERVER__SECRET_KEY
#     value: "my_super_secret_key_123"
#   - name: ENTSOE_API_KEY
#     value: "808aeda6-8be2-421e-bfca-2165074d69a1"

# airflow:
#   config:
#     AIRFLOW__CORE__EXECUTOR: "LocalExecutor"
#     AIRFLOW__CORE__LOAD_EXAMPLES: "False"
#     AIRFLOW__API__AUTH_BACKENDS: "airflow.api.auth.backend.basic_auth"
#     AIRFLOW__WEBSERVER__RBAC: "true"
