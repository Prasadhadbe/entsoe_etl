from datetime import datetime, timedelta

def get_daily_chunks(start: str, end: str):
    chunks = []
    current = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")

    while current <= end_dt:
        day = current.strftime("%Y-%m-%d")
        chunks.append({"start_date": day, "end_date": day})
        current += timedelta(days=1)
    return chunks

