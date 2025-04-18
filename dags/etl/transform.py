import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def transform_data(**kwargs):
    ti = kwargs["ti"]
    raw_xml = ti.xcom_pull(task_ids="extract_data", key="raw_xml")

    root = ET.fromstring(raw_xml)
    ns = {"ns": "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0"}

    all_prices = []

    for timeseries in root.findall(".//TimeSeries"):
        period = timeseries.find(".//Period")
        start = period.find("timeInterval/start").text
        resolution = period.find("resolution").text

        base_time = datetime.strptime(start, "%Y-%m-%dT%H:%MZ")

        for point in period.findall("Point"):
            pos = int(point.find("position").text)
            price = float(point.find("price.amount").text)
            timestamp = base_time + timedelta(minutes=15 * (pos - 1))

            all_prices.append({
                "timestamp": timestamp.isoformat(),
                "price_eur_per_mwh": price
            })

    ti.xcom_push(key="transformed_data", value=all_prices)
