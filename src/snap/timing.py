from datetime import datetime
import asyncio

def now():
    return datetime.now().timestamp()

time_start = now()

def now_rel():
    return now()-time_start

async def wait_until(t, dtmin=0):
    dt = max(t-now(),dtmin)
    await asyncio.sleep(max(dt,dtmin))

