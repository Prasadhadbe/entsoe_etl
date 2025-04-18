import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from airflow.models import Variable

load_dotenv()
API_KEY = os.getenv("808aeda6-8be2-421e-bfca-2165074d69a1")

# ✅ Load API key from environment variable (make sure it's named correctly)
API_KEY = os.getenv("ENTSOE_API_KEY")

# Germany EIC code for BZN
GERMANY_BZN_EIC = "10Y1001A1001A83F"
print(os.getenv("ENTSOE_API_KEY"))


# Mock TaskInstance with xcom_push behavior
class MockTI:
    def xcom_push(self, key, value):
        print(f"[Mock XCom] {key} = {value[:200]}...")  # Preview of value

def extract_data(**kwargs):
    execution_date = kwargs['ds']
    date_obj = datetime.strptime(execution_date, "%Y-%m-%d")
    date_str = date_obj.strftime("%Y%m%d")

    # Load token and strip whitespace
    API_KEY = os.getenv("ENTSOE_API_KEY", "").strip()

    print(f"Fetching ENTSOE Day-Ahead Prices for {date_str}")
    print(f"Token: '{API_KEY}'")  # Debug

    url = "https://web-api.tp.entsoe.eu/api"
    params = {
        "documentType": "A44",
        "in_Domain": GERMANY_BZN_EIC,
        "out_Domain": GERMANY_BZN_EIC,
        "periodStart": f"{date_str}0000",
        "periodEnd": f"{date_str}2300",
        "securityToken": API_KEY
    }

    response = requests.get(url, params=params)
    print("Final Request URL:", response.url)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}, {response.text}")

    kwargs['ti'].xcom_push(key='raw_xml', value=response.text)



# Define the function exactly as you wrote
# def extract_data(**kwargs):
#     execution_date = kwargs['ds']
#     date_obj = datetime.strptime(execution_date, "%Y-%m-%d")
#     date_str = date_obj.strftime("%Y%m%d")
#     API_KEY = "808aeda6-8be2-421e-bfca-2165074d69a1"
#     print(f"Fetching ENTSOE Day-Ahead Prices for {date_str}")

#     # url = "https://web-api.tp.entsoe.eu/api"
#     # params = {
#     #     'documentType': 'A44',  # Day-ahead prices
#     #     'in_Domain': GERMANY_BZN_EIC,
#     #     'out_Domain': GERMANY_BZN_EIC,
#     #     'periodStart': f"{date_str}0000",
#     #     'periodEnd': f"{date_str}2359",
#     #     'securityToken': API_KEY
#     # }

#     # print("Requesting URL with params:", url, params)

#     response = requests.get("""https://web-api.tp.entsoe.eu/api?documentType=A44&in_Domain=10Y1001A1001A83F&out_Domain=10Y1001A1001A83F&periodStart=202404170000&periodEnd=202404172300&securityToken=808aeda6-8be2-421e-bfca-2165074d69a1""")
#     # response = requests.get(url, params=params)

#     print("Final Request URL:", response.url)

#     if response.status_code != 200:
#         raise Exception(f"API Error: {response.status_code}, {response.text}")

#     kwargs['ti'].xcom_push(key='raw_xml', value=response.text)

# # Run test
# dummy_kwargs = {
#     'ds': '2024-01-01',
#     'ti': MockTI()
# }

# extract_data(**dummy_kwargs)



# import os
# import requests
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# from airflow.models import Variable
# from airflow.utils.dates import days_ago
# from airflow.models import TaskInstance


# load_dotenv()
# API_KEY = os.getenv("808aeda6-8be2-421e-bfca-2165074d69a1")

# # Germany EIC code for BZN: 10Y1001A1001A83F
# GERMANY_BZN_EIC = "10Y1001A1001A83F"

# def extract_data(**kwargs):
#     # Get execution date from Airflow
#     execution_date = kwargs['ds']
#     date_obj = datetime.strptime(execution_date, "%Y-%m-%d")
#     date_str = date_obj.strftime("%Y%m%d")

#     print(f"Fetching ENTSOE data for date: {date_str}")


#     # Example: Day-Ahead Prices Endpoint
#     url = (
#         f"https://transparency.entsoe.eu/api?"
#         f"documentType=A44&in_Domain={GERMANY_BZN_EIC}&out_Domain={GERMANY_BZN_EIC}"
#         f"&periodStart={date_str}0000&periodEnd={date_str}2300&securityToken={API_KEY}"
#     )
#     print(url)
#     response = requests.get(url)
#     if response.status_code != 200:
#         raise Exception(f"API Error: {response.status_code}, {response.text}")
    
#     # Save raw response to XCom for now
#     kwargs['ti'].xcom_push(key='raw_xml', value=response.text)

# # extract_data()
# # def extract_data(**kwargs):
# #     with open('dags/mock_data/day_ahead_prices.xml', 'r') as f:
# #         xml = f.read()
# #     # Save raw response to XCom for now
# #     kwargs['ti'].xcom_push(key='raw_xml', value=xml)





