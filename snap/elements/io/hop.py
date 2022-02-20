"""
===================
Hopskotch interface
===================

Wrapper around `hop-client <https://github.com/scimma/hop-client>`_ module
"""

import hop
import asyncio 
from functools import partial
from concurrent.futures import ThreadPoolExecutor

import logging
logger = logging.getLogger(__name__)

async def astream(s):
    gen = s.read()
    def get_message():
        return next(gen)

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        while True:
            msg = await loop.run_in_executor(pool, get_message)
            yield msg

async def recv(address: str, auth: bool=True):
    """ 
    Data :term:`source`.
    Receive messages from hopskotch.

    Args:
       address:
            hopskotch location of the format ``kafka://<host>:<port>/<topic>`` to subscribe
       auth: 
            use hopskotch authentication
    Yields:
        received message
    """

    while True:
        try:
            logger.info(f'Connecting to {address}...')
            with hop.Stream(auth=auth).open(address, 'r') as s:
                async for msg in astream(s):
                    yield msg
        except ValueError as e:
            logger.error(e)

def send(address: str, auth: bool=True):
    """ 
    Processing :term:`step`.
    Send messages to hopskotch.

    Args:
       address
            hopskotch location of the format ``kafka://<host>:<port>/<topic>`` to publish
       auth: 
            use hopskotch authentication
    :Input:
        data(any JSON-serializable object) to be sent
    :Output:
        data unchanged
    """
    s = hop.Stream(auth=auth).open(address, 'w')
    
    def _f(data):
        try:
            s.write(data)
            return data
        except ValueError:
            logger.error(e)
    return _f

