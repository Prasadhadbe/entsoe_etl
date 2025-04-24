import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz

def transform_data(raw_xml, target_resolution="PT60M", truncate_preview=True, is_daily =False):
    ns = {"ns": "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3"}

    # Validate target resolution
    if target_resolution not in ("PT60M", "PT15M"):
        print(f"❌ Invalid target resolution: {target_resolution}. Must be PT60M or PT15M")
        return []

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
    print(f"🚀 Starting transformation (keeping only {target_resolution} data)...")

    # CET timezone (handles DST automatically)
    cet = pytz.timezone("Europe/Berlin")

    for timeseries in root.findall(".//ns:TimeSeries", ns):
        period = timeseries.find("ns:Period", ns)
        if period is None:
            print("⚠️ Skipping TimeSeries: no Period found")
            continue

        resolution_elem = period.find("ns:resolution", ns)
        if resolution_elem is None or resolution_elem.text != target_resolution:
            continue

        start_elem = period.find("ns:timeInterval/ns:start", ns)
        if start_elem is None:
            print("⚠️ Skipping TimeSeries: missing start time")
            continue

        try:
            base_time_naive = datetime.strptime(start_elem.text, "%Y-%m-%dT%H:%MZ")
            # Attach CET timezone and convert to UTC
            base_time_cet = cet.localize(base_time_naive.replace(tzinfo=None), is_dst=None)
            # base_time_utc = base_time_cet.astimezone(pytz.utc)
        except Exception as e:
            print(f"⚠️ Time parsing/conversion error: {e}")
            continue

        interval_minutes = 60 if target_resolution == "PT60M" else 15

        for point in period.findall("ns:Point", ns):
            try:
                pos = int(point.find("ns:position", ns).text)
                price = float(point.find("ns:price.amount", ns).text)
                timestamp = base_time_cet + timedelta(minutes=interval_minutes * (pos - 1))
                all_prices.append({
                    "timestamp": timestamp.isoformat(),
                    "price_eur_per_mwh": price
                })

            except Exception as e:
                print(f"⚠️ Skipping point due to error: {e}")
                continue
        if is_daily and len(all_prices) > 24:
            print(f"⚠️ Got {len(all_prices)} entries, trimming to 24...")
            all_prices = all_prices[:24]

    print(f"✅ Transformed {len(all_prices)} {target_resolution} price points.")
    return all_prices
