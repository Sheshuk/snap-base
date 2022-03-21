"""
=================
ZeroMQ  interface
=================

Wrapper around `pyzmq <https://github.com/zeromq/pyzmq>`_ module
"""

import asyncio
import zmq.asyncio

import logging
logger = logging.getLogger(__name__)

async def recv(address: str):
    """
    Data :term:`source`.
    Receive data from zmq.PULL socket on given address.
    

    Args:
        address: 
            socket address to *bind*, in format ``<protocol>/<address>:<port>``,
            for example ``tcp:/127.0.0.1:9000``

    Yields: 
        received message
    """
    with zmq.asyncio.Context() as ctx:
        with ctx.socket(zmq.PULL) as s:
            logger.info(f'Listen to address="{address}"')
            s.bind(address) 
            while True:
                data = await s.recv_pyobj()
                logger.debug(f'RECV:: "{data}"')
                yield data

def send(address: str):
    """
    Processing  :term:`step`.
    Send data to given addresses via zmq.PUSH socket

    Args:
        address: 
            socket address to *connect*, in format ``<protocol>/<address>:<port>``, 
            for example ``tcp:/127.0.0.1:9000``
    :Input:
        data(any pickle-serializable object) to be sent
    :Output:
        data unchanged
    """ 
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

