"""
Timing elements
===============
"""
from snap.timing import now,wait_until

def every(seconds):
    """ 
    Can be either a :term:`source`, or a :term:`step`.

    * As a source: produce "True" values with given minimum delay.
    * As a step: get the data from previous step and forward it downstream with given minimum delay.
    
    Args:
        seconds (float)
            Minimal delay between iterations.

    :Input: (if source)
        anything
    :Output:
        data unchanged
    """
    async def _dummy_source():
        while True:
            yield True

    async def _f(source=_dummy_source):
        t0 = now()
        async for data in source:
            yield data
            t0+=seconds
            await wait_until(t0)
    return _f
    
