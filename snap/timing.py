import time
import asyncio

time_start = time.time()
def now():
    return time.time()-time_start

async def wait_until(t, dtmin=0):
    dt = t-now()
    await asyncio.sleep(max(dt,dtmin))

