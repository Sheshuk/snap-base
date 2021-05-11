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

async def recv(address: str, auth: bool=False):
    """ Receive messages from hopskotch (source)
    Args:
        address: hopskotch location of the format 'kafka://{host}:{port}/{topic} to subscribe
        auth: use hopskotch authentication (default: false)
    Yields:
        received message
    """
    stream = hop.Stream(auth=auth, persist=True)

    while True:
        try:
            logger.info(f'Connecting to {address}...')
            with stream.open(address, 'r') as s:
                async for msg in astream(s):
                    yield msg
        except ValueError as e:
            logger.error(e)

def send(address: str, auth: bool=False):
    """ Send messages to hopskotch (step)
        Args:
           address: hopskotch location of the format 'kafka://{host}:{port}/{topic} to publish
           auth: use hopskotch authentication (default: false)
    """
    stream = hop.Stream(auth=None)
    s = stream.open(address, 'w')
    
    def _f(data):
        try:
            s.write(data)
        except ValueError:
            logger.error(e)
    return _f

