import asyncio
import zmq.asyncio

import logging
logger = logging.getLogger(__name__)

from time import perf_counter as now
async def status_server(address, status=b'OK'):
    """A server, which replies with current status on each request"""

    get_status = status if callable(status) else lambda: status

    with zmq.asyncio.Context() as ctx:
        with ctx.socket(zmq.REP) as s:
            logger.info(f'Listen to address="{address}"')
            s.bind(address)
            while True:
                req = await s.recv()
                logger.debug(f'request="{req}"')
                await s.send(get_status())

async def status_req(address, timeout=1):
    with zmq.asyncio.Context() as ctx:
        while True:
            try:
                with ctx.socket(zmq.REQ) as s:
                    logger.info(f'Connect to address="{address}"')
                    s.connect(address)
                    while True:
                        t0 = now()
                        await s.send(b'STATUS')
                        rep = await asyncio.wait_for(s.recv(), timeout=timeout)
                        logger.debug(f'reply="{rep}"')
                        yield rep, now()-t0
            except asyncio.TimeoutError:
                yield b'TIMEOUT',now()-t0
                
