import asyncio
import zmq.asyncio

import logging
logger = logging.getLogger(__name__)

async def recv(address):
    """receive data from zmq.PULL socket on given address"""
    with zmq.asyncio.Context() as ctx:
        with ctx.socket(zmq.PULL) as s:
            logger.info(f'Listen to address="{address}"')
            s.bind(address) 
            while True:
                data = await s.recv_pyobj()
                logger.debug(f'RECV:: "{data}"')
                yield data

def send(address):
    """send data to given addresses via zmq.PUSH socket""" 
    if isinstance(address, str):
        address=[address]
    async def _f(source):
        #create the context
        with zmq.asyncio.Context() as ctx:
            #initialize the sockets
            socks = [ctx.socket(zmq.PUSH) for a in address]
            #connect sockets
            for s,addr in zip(socks,address):
                logger.info(f'Connect to address="{addr}"')
                s.connect(addr)
                
            try:
                #start the work
                logger.debug('waiting for data to send...')
                async for data in source:
                    logger.debug(f'SEND:: "{data}"')
                    await asyncio.gather(*[s.send_pyobj(data) for s in socks])
                    yield data
            finally:
                #close sockets
                for s in socks:
                    s.close()
    return _f

