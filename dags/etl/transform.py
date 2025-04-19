import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


def transform_data(raw_xml, truncate_preview=True):
    ns = {"ns": "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3"}

    if not raw_xml:
        print("❌ No raw XML provided!")
        return []

    if truncate_preview:
        print(f"📥 Raw XML received (preview):\n{raw_xml[:500]}...")
    else:
        print(f"📥 Raw XML received:\n{raw_xml}")

    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as e:
        print(f"❌ Failed to parse XML: {e}")
        return []

    all_prices = []
    print("🚀 Starting transformation...")

    for timeseries in root.findall(".//ns:TimeSeries", ns):
        period = timeseries.find("ns:Period", ns)
        if period is None:
            print("⚠️ Skipping TimeSeries: no Period found")
            continue

        start_elem = period.find("ns:timeInterval/ns:start", ns)
        resolution_elem = period.find("ns:resolution", ns)

        if start_elem is None or resolution_elem is None:
            print("⚠️ Skipping TimeSeries: missing start/resolution")
            continue

        try:
            base_time = datetime.strptime(start_elem.text, "%Y-%m-%dT%H:%MZ")
        except ValueError:
            print(f"⚠️ Invalid start time format: {start_elem.text}")
            continue

        resolution = resolution_elem.text
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
                    "timestamp": timestamp,
                    "price_eur_per_mwh": price
                })
            except Exception as e:
                print(f"⚠️ Skipping point due to error: {e}")
                continue

    print(f"✅ Transformed {len(all_prices)} price points.")
    return all_prices


