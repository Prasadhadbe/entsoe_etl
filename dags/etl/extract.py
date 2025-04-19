import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
from typing import Optional
from airflow.models import Variable

# Load environment variables
load_dotenv()

# Constants
GERMANY_BZN_EIC = "10Y1001A1001A82H"  # DE_LU Germany_Luxemburg
ENTSOE_API_URL = "https://web-api.tp.entsoe.eu/api"

def get_api_key() -> str:
    """Retrieve API key from environment variables with validation."""
    api_key = os.getenv("ENTSOE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ENTSOE_API_KEY environment variable not set or empty")
    return api_key

def validate_dates(start: datetime, end: datetime) -> None:
    """Validate that dates are proper datetime objects and in correct order."""
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        raise TypeError("start_date and end_date must be datetime objects")
    if start > end:
        raise ValueError("start_date cannot be after end_date")
    if (end - start) > timedelta(days=7):  # ENTSOE typically has 7-day limit
        logging.warning("Requesting data for more than 7 days - might hit API limits")

def extract_data(**kwargs) -> str:
    """
    Extract day-ahead prices from ENTSOE API.
    
    Args:
        start_date: Start datetime object (required)
        end_date: End datetime object (required)
        resolution: Time resolution (default: "PT15M")
        ti: Airflow TaskInstance (automatically passed)
    
    Returns:
        Raw XML response as string
    
    Raises:
        ValueError: For missing/invalid parameters
        Exception: For API request failures
    """
    try:
        # Get and validate parameters
        start = kwargs.get('start_date')
        end = kwargs.get('end_date')
        if None in (start, end):
            raise ValueError("Both start_date and end_date must be provided")
        
        validate_dates(start, end)
        
        resolution = kwargs.get("resolution", "PT15M")
        api_key = get_api_key()
        
        logging.info(f"Fetching ENTSOE Day-Ahead Prices from {start} to {end}")
        logging.info(f"resolution(not applied): {resolution}")
        logging.debug(f"Using resolution: {resolution}")

        # Prepare API request
        params = {
            "documentType": "A44",
            "periodStart": start.strftime("%Y%m%d%H%M"),
            "periodEnd": end.strftime("%Y%m%d%H%M"),
            "out_Domain": GERMANY_BZN_EIC,
            "in_Domain": GERMANY_BZN_EIC,
            "securityToken": api_key
        }

        # Make API request with timeout
        try:
            response = requests.get(
                ENTSOE_API_URL,
                params=params,
                timeout=30  # 30 seconds timeout
            )
            logging.debug(f"API Request URL: {response.url}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

        # Validate response
        if response.status_code != 200:
            error_msg = f"API Error {response.status_code}"
            if response.text:
                error_msg += f": {response.text[:500]}"  # Include first 500 chars of error
            raise Exception(error_msg)

        # Push to XCom and return
        xml_response = response.text
        kwargs['ti'].xcom_push(key='raw_xml', value=xml_response)
        logging.info(f"Successfully extracted {len(xml_response)} bytes of XML data")
        logging.debug(f"XML snippet: {xml_response[:200]}...")
        
        return xml_response

    except Exception as e:
        logging.error(f"Extraction failed: {str(e)}")
        raise



# import os
# import requests
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# from airflow.models import Variable

# load_dotenv()
# # API_KEY = os.getenv("808aeda6-8be2-421e-bfca-2165074d69a1")

# # ✅ Load API key from environment variable (make sure it's named correctly)
# API_KEY = os.getenv("ENTSOE_API_KEY")

# # Germany EIC code for BZN
# GERMANY_BZN_EIC = "10Y1001A1001A82H" #	DE_LU	Germany_Luxemburg
# print(os.getenv("ENTSOE_API_KEY"))

# # # Mock TaskInstance with xcom_push behavior
# # class MockTI:
# #     def xcom_push(self, key, value):
# #         print(f"[Mock XCom] {key} = {value[:200]}...")  # Preview of value

# def extract_data(**kwargs):
#     start = kwargs.get('start_date')
#     end = kwargs.get('end_date')
    
#     start_str = start.strftime("%Y%m%d%H%M")
#     end_str = end.strftime("%Y%m%d%H%M")
 
#     print(start_str)
#     print(end_str)
#     # end = kwargs.get('end_date', start + timedelta(days=1))    
#     resolution = kwargs.get("resolution", "PT15M")

    
#     # Load token and strip whitespace
#     API_KEY = os.getenv("ENTSOE_API_KEY", "").strip()

#     print(f"Fetching ENTSOE Day-Ahead Prices from {start} to {end}")
#     print(f"Token: '{API_KEY}'")  # Debug

#     url = "https://web-api.tp.entsoe.eu/api"
#     params = {
#         "documentType": "A44",
#         "periodStart": start.strftime("%Y%m%d%H%M"),
#         "periodEnd": end.strftime("%Y%m%d%H%M"),
#         "out_Domain": GERMANY_BZN_EIC,
#         "in_Domain": GERMANY_BZN_EIC,
#         "securityToken": API_KEY
#     }

#     response = requests.get(url, params=params)
#     print("Final Request URL:", response.url)

#     if response.status_code != 200:
#         raise Exception(f"API Error: {response.status_code}, {response.text}")

#     kwargs['ti'].xcom_push(key='raw_xml', value=response.text)
#     print("Extracted XML snippet:", response.text[:500])

# dummy_kwargs = {
#     "start_date": datetime(2024, 1, 1),
#     "end_date": datetime(2024, 3, 1),
#     'ti': MockTI()
# }

# extract_data(**dummy_kwargs)



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





