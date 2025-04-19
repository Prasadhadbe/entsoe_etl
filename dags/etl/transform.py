import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def transform_data(**kwargs):
    ti = kwargs["ti"]
    raw_xml = ti.xcom_pull(task_ids="extract_data", key="raw_xml")
    print(f"📥 Raw XML received:\n{raw_xml[:500]}...")

    root = ET.fromstring(raw_xml)
    ns = {"ns": "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3"}  # Updated namespace

    all_prices = []
    print("Starting transformation!")

    for timeseries in root.findall(".//ns:TimeSeries", ns):
        period = timeseries.find("ns:Period", ns)
        if period is None:
            print("⚠️ Skipping incomplete TimeSeries (no Period)")
            continue

        start_elem = period.find("ns:timeInterval/ns:start", ns)
        resolution_elem = period.find("ns:resolution", ns)

        if start_elem is None or resolution_elem is None:
            print("⚠️ Skipping incomplete TimeSeries (missing start/resolution)")
            continue

        start = start_elem.text
        resolution = resolution_elem.text

        try:
            base_time = datetime.strptime(start, "%Y-%m-%dT%H:%MZ")
        except ValueError:
            print(f"⚠️ Invalid time format: {start}")
            continue

        if resolution == "PT60M":
            interval_minutes = 60
        elif resolution == "PT15M":
            interval_minutes = 15
        else:
            print(f"⚠️ Unsupported resolution: {resolution}")
            continue

        for point in period.findall("ns:Point", ns):
            try:
                pos = int(point.find("ns:position", ns).text)
                price = float(point.find("ns:price.amount", ns).text)
                timestamp = base_time + timedelta(minutes=interval_minutes * (pos - 1))
                all_prices.append({
                    "timestamp": timestamp.isoformat(),
                    "price_eur_per_mwh": price
                })
            except Exception as e:
                print(f"⚠️ Skipping point due to error: {e}")
                continue

    print(f"✅ Transformed {len(all_prices)} price points.")
    return all_prices
