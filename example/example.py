import asyncio
from datetime import datetime
import time
import numpy as np

from snap import timing

#generator example
async def random(mean=0, sigma=1):
    """generate numbers with gaussian distriution
    """
    while True:
        yield np.random.normal(loc=mean, scale=sigma)

# filter example: threshold
def threshold(val=0):
    """ yield values above 'val' """
    async def _f(source):
        async for d in source:
            if(d>val): 
                yield d
    return _f

#buffer object example
class Buffer:
    def __init__(self):
        """object to accumulate the data in the time bins"""
        self.data = []
    async def put(self, data):
        self.data+=[data]

    async def get(self):
        res = self.data
        self.data = []
        return res

#function without parameters
def count(d):
    return len(d)

#heavy blocking function for parallel processing
def blocking(delay=10):
    def _f(d):
        time.sleep(delay)
        return d
    return _f

async def gen_timestamp():
    while True:
        yield datetime.now()

def timestamp_to_json(ts):
    return {'timestamp':int(datetime.timestamp(ts)*1e6)}

def timestamp_from_json(msg):
    ts = msg['timestamp']/1e6 #convert to seconds
    return datetime.fromtimestamp(ts)

def to_str(data):
    return str(data)

def measure_latency(ts):
    dt = datetime.now()-ts
    return dt.total_seconds()
