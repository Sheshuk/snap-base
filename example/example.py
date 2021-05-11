import numpy as np
import asyncio
import datetime
import time

#generator example
async def random_walk(start=0, sigma=1, delay=1):
    """generate numbers with gaussian random walk
    params:
        * start: start value
        * sigma: sigma of the random step
        * delay: time between numbers in seconds
    """
    x = start
    while True:
        x+=np.random.normal(loc=0, scale=sigma)
        await asyncio.sleep(delay)
        yield x

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
    def __init__(self, buffer_time=10):
        """object to accumulate the data in the time bins"""
        self.data = []
        self.buffer_time = buffer_time
    async def put(self, data):
        self.data+=[data]

    async def get(self):
        await asyncio.sleep(self.buffer_time)
        res = self.data
        self.data = []
        return res

#function with parameters
def dump_with_timestamp(fmt="%X"):
    def _f(d):
        t = datetime.datetime.now()
        print(f'{t.strftime(fmt)}: {d}')
        return d
    return _f

#function with parameters
def dump(prefix="DUMP"):
    def _f(d):
        print(f'{prefix} {d}')
        return d
    return _f

#function without parameters
def count(d):
    return len(d)

#heavy blocking function for parallel processing
def blocking(delay=10):
    def _f(d):
        time.sleep(delay)
        return d
    return _f

async def gen_timestamp(delay=1):
    while True:
        await asyncio.sleep(delay)
        yield datetime.datetime.now()

def to_str(data):
    return str(data)

def measure_latency(ts):
    dt = datetime.datetime.now()-ts
    return dt
