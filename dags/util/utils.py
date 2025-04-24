from datetime import datetime, timedelta

def get_weekly_chunks(start: str, end: str):
    chunks = []
    current = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")

    while current < end_dt:
        next_dt = min(current + timedelta(days=31), end_dt) #backfilling from 2024-01-01 by months 
        chunks.append({
            "start_date": current.strftime("%Y-%m-%d"),
            "end_date": next_dt.strftime("%Y-%m-%d")
        })
        current = next_dt
    return chunks
