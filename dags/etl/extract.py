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

def extract_data(start_date: Optional[str] = None, end_date: Optional[str] = None, resolution: str = "PT15M", **kwargs) -> str:
    """
    Extract day-ahead prices from ENTSOE API.

    Args:
        start_date: Start date string in YYYY-MM-DD format (required)
        end_date: End date string in YYYY-MM-DD format (required)
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
        if not start_date or not end_date:
            raise ValueError("Both start_date and end_date must be provided")

        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        validate_dates(start, end)
        api_key = get_api_key()

        logging.info(f"Fetching ENTSOE Day-Ahead Prices from {start} to {end}")
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

        try:
            response = requests.get(
                ENTSOE_API_URL,
                params=params,
                timeout=30
            )
            logging.debug(f"API Request URL: {response.url}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

        if response.status_code != 200:
            error_msg = f"API Error {response.status_code}"
            if response.text:
                error_msg += f": {response.text[:500]}"
            raise Exception(error_msg)

        xml_response = response.text
        if 'ti' in kwargs:
            kwargs['ti'].xcom_push(key='raw_xml', value=xml_response)

        logging.debug(f"XML snippet: {xml_response[:200]}...")

        return xml_response

    except Exception as e:
        logging.error(f"Extraction failed: {str(e)}")
        raise


# test_chunk = {"start_date": '2024-01-01', 'end_date': '2024-01-08'}
# extract_data(**test_chunk)