from datetime import datetime, timedelta

def get_monthly_chunks(start: str, end: str):
    chunks = []
    current = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")

    while current < end_dt:
        # Move to the same day next month
        if current.month == 12:
            next_dt = datetime(current.year + 1, 1, 1)
        else:
            next_dt = datetime(current.year, current.month + 1, 1)

        # Clip to end date
        next_dt = min(next_dt, end_dt)
        chunks.append({
            "start_date": current.strftime("%Y-%m-%d"),
            "end_date": next_dt.strftime("%Y-%m-%d")
        })
        current = next_dt
    # chunks = []
    # current = datetime.strptime(start, "%Y-%m-%d")
    # end_dt = datetime.strptime(end, "%Y-%m-%d")

    # while current < end_dt:
    #     next_dt = min(current + timedelta(days=7), end_dt) #backfilling from 2024-01-01 by months 
    #     chunks.append({
    #         "start_date": current.strftime("%Y-%m-%d"),
    #         "end_date": next_dt.strftime("%Y-%m-%d")
    #     })
    #     current = next_dt
    return chunks